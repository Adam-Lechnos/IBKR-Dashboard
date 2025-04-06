import requests
import datetime
import socket
import psutil
import os
import sys
import time
import pytz
import csv
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# If first argument is present, honor it as time in seconds to re-execute the function, otherwise default to every 1800 seconds (30 minutes)
# Maximum honored first argument is 86400 seconds (1 day)
# try:
#     if int(sys.argv[1])>0:
#         sleepTimeSeconds=min(int(sys.argv[1]), 86400)
# except: 
#         sleepTimeSeconds=1800

sleepTimeSeconds = int(os.environ.get('sleepTimeSeconds'))
csvFileName = os.environ.get('csvFileName')
webPageTitle = os.environ.get('webPageTitle')
if webPageTitle == None: webPageTitle = 'IBKR Dashboard'
if sleepTimeSeconds == None: sleepTimeSeconds = 60
if csvFileName == None: csvFileName = 'IBKR_Data'
# set webpage refresh time by extra seconds passed program refresh interval
refreshPageSeconds=sleepTimeSeconds+5

# Parse IP from ip-addr.txt within the IBeam container via shared volume mount
ipFile="/var/ibkr/util-data/ip-addr.txt"
if os.path.isfile(ipFile):
    with open("/var/ibkr/util-data/ip-addr.txt", "r") as f:
        IBeam = f.readline().rstrip()
else:
    print(f"Unable to locate '/var/ibkr/util-data/ip-addr.txt' in shared volume mount for IBeam container IP. May be a K8s cluster", file=sys.stderr)
    IBeam="ibeam"

def parseAPICreateWebFiles(today):
    columnDataRisk = ['RISK DATA']
    columnDataPos = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((f'{IBeam}',5000))
    if result == 0:
        print(f"({today}) Connection to IBeam container successful.. parsing IBKR API and creating Web files")
    else:
        print(f"({today}) Connection to IBeam container failed, retrying in {sleepTimeSeconds} seconds..", file=sys.stderr); return
    sock.close()

    uptime=round(time.clock_gettime(time.CLOCK_BOOTTIME)/60,2)
    systemUsage=(f"CPU {psutil.cpu_percent(4)}% :: RAM {psutil.virtual_memory()[2]}%")
    grandTotalMarginBalance=0
    grandTotalNetLiquidationVal=0
    grandTotalExcessLiquidity=0
    fileList = []

    response = requests.get('https://{IBeam}:5000/v1/api/portfolio/accounts'.format(IBeam=IBeam), verify=False)
    if response.status_code != 200: print(f'({today}) Connection to IBKR API for Main Data did not return 200, retrying in {sleepTimeSeconds} seconds..', file=sys.stderr); return
    data=response.json()
    
    columnDataCsv = open(f"/usr/src/app/webserver/static/{csvFileName}_temp.csv", "w+", newline='')
    wr = csv.writer(columnDataCsv, quoting=csv.QUOTE_ALL)
    f = open("/usr/src/app/webserver/static/index_temp.html", "w+"); fileList.append("/usr/src/app/webserver/static/index_temp.html")
    f.write(f'<html> <head> <title>{webPageTitle}</title> <link rel="shortcut icon" href="./favicon.ico"> <meta http-equiv="refresh" content="{refreshPageSeconds}"\/> </head> <body>')
    f.write("<pre>")
    f.write('<img src="./images/interactive-brokers.svg" alt="Interactive Brokers" border="0" loading="lazy" width="200" height="40" />')
    f.write('<br><br><hr>')
    f.write('<h3>Margin Risk Data</h3>')
    for i in range(len(data)):
        accountId=data[i]['id']
        responseGAS = requests.get('https://{IBeam}:5000/v1/api/iserver/account/{accountId}/summary'.format(accountId=accountId, IBeam=IBeam), verify=False)
        if responseGAS.status_code != 200: print(f'({today}) Connection to IBKR API for Margin Risk Data did not return 200, retrying in {sleepTimeSeconds} seconds..', file=sys.stderr); return
        dataGAS=responseGAS.json()
        accountName=data[i]['accountAlias']
        filenameRisk=accountName.replace(" ","-")
        fRisk = open(f"/usr/src/app/webserver/static/Risk-{filenameRisk}_temp.html", "w+"); fileList.append(f"/usr/src/app/webserver/static/Risk-{filenameRisk}_temp.html")
        fRisk.write(f'<html> <head> <title>{webPageTitle}: Margin Risk: {accountName}</title> <link rel="shortcut icon" href="./favicon.ico"> <meta http-equiv="refresh" content="{refreshPageSeconds}"\/> </head> <body>')
        fRisk.write('<pre>')
        accountId='************'+accountId[-2:]
        f.write(f'<h4>Account Name: {accountName}, Account ID: {accountId}</h4>')
        f.write(f'<a href="./Risk-{filenameRisk}.html">{accountName}</a>\n')
        fRisk.write(f'<h4>Margin Risk Data | Account Name: {accountName}, Account ID: {accountId} | Last Updated: {today}</h4>')
        fRisk.write('<a href="./">Dashboard</a>\n')
        balance=dataGAS['balance']
        sma=dataGAS['SMA']
        buyingPower=dataGAS['buyingPower']
        netLiquidationValue=dataGAS['netLiquidationValue']
        equityWithLoanValue=dataGAS['equityWithLoanValue']
        totalCashValue=dataGAS['totalCashValue']
        excessLiquidity=dataGAS['excessLiquidity']
        maintenanceMargin=dataGAS['maintenanceMargin']

        if totalCashValue < 0: grandTotalMarginBalance+=totalCashValue
        grandTotalNetLiquidationVal+=netLiquidationValue
        grandTotalExcessLiquidity+=excessLiquidity

        balanceCol = "green" if (balance >= 0) else "red"
        totalCashValueCol = "green" if (totalCashValue > 0) else "red"
        nlvCol = "green" if (netLiquidationValue >= 0) else "red"
        elvCol = "green" if (equityWithLoanValue >= 0) else "red"
        smaCol = "green" if (sma >= 0) else "red"
        buyingPowerCol = "green" if (buyingPower >= 0) else "red"
        maintenanceMarginCol = "green" if (maintenanceMargin >= 0) else "red"
        excessLiquidityCol = "green" if (excessLiquidity >= 0) else "red"

        f.write('-'*177)
        f.write('\n')
        f.write(f'| {"Balance: $":>25s} <font color="{balanceCol}">{balance:>15.2f}</font> | {"SMA: $":>25s} <font color="{smaCol}">{sma:>15.2f}</font> | {"Buying Power: $":>25s} <font color="{buyingPowerCol}">{buyingPower:>15.2f}</font> | {"Net Liquidation Value: $":>25s} <font color="{nlvCol}">{netLiquidationValue:>15.2f}</font> |\n')
        f.write(f'| {"Total Cash Value: $":>25s} <font color="{totalCashValueCol}">{totalCashValue:>15.2f}</font> | {"Excess Liquidity: $":>25s} <font color="{excessLiquidityCol}">{excessLiquidity:>15.2f}</font> | {"Maintenance Margin: $":>25s} <font color="{maintenanceMarginCol}">{maintenanceMargin:>15.2f}</font> | {"Equity With Loan Value: $":>25s} <font color="{elvCol}">{equityWithLoanValue:>15.2f}</font> |')
        f.write('\n')
        f.write('-'*177)
        
        totalCashValuePerAccount = 0
        if totalCashValue < 0: totalCashValuePerAccount = totalCashValue

        marginCus = ((excessLiquidity/netLiquidationValue) * 100)
        marginPer = (((totalCashValuePerAccount * -1)/netLiquidationValue) * 100)
        netLiquidationValCol="green" if (grandTotalNetLiquidationVal >= 0) else "red"
        totalCashValuePerAccountCol="red" if (grandTotalMarginBalance < 0) else "green"
        marginCusCol = "green" if (marginCus >= 50) else "red"
        marginPerCol = "green" if (marginPer <= 12) else "red"
        fRisk.write('\n<b>')
        fRisk.write(f'{"Account Net Liquidation Value: $":>32s} <font color="{netLiquidationValCol}">{netLiquidationValue:>15.2f}</font>')
        fRisk.write('\n')
        fRisk.write(f'{"Account Margin Balance: $":>32s} <font color="{totalCashValuePerAccountCol}">{totalCashValuePerAccount:>15.2f}</font>')
        fRisk.write('\n\n')
        fRisk.write(f'{"Margin Cushion:  ":>32s} <font color="{marginCusCol}">{marginCus:>14.2f}%</font>')
        fRisk.write('\n')
        fRisk.write(f'{"Margin Percent NLV:  ":>32s} <font color="{marginPerCol}">{marginPer:>14.2f}%</font>\n\n')
        fRisk.write('</b>')
        fRisk.write('-'*177)
        fRisk.write('\n')
        fRisk.write(f'| {"Balance: $":>25s} <font color="{balanceCol}">{balance:>15.2f}</font> | {"SMA: $":>25s} <font color="{smaCol}">{sma:>15.2f}</font> | {"Buying Power: $":>25s} <font color="{buyingPowerCol}">{buyingPower:>15.2f}</font> | {"Net Liquidation Value: $":>25s} <font color="{nlvCol}">{netLiquidationValue:>15.2f}</font> |\n')
        fRisk.write(f'| {"Total Cash Value: $":>25s} <font color="{totalCashValueCol}">{totalCashValue:>15.2f}</font> | {"Excess Liquidity: $":>25s} <font color="{excessLiquidityCol}">{excessLiquidity:>15.2f}</font> | {"Maintenance Margin: $":>25s} <font color="{maintenanceMarginCol}">{maintenanceMargin:>15.2f}</font> | {"Equity With Loan Value: $":>25s} <font color="{elvCol}">{equityWithLoanValue:>15.2f}</font> |')
        fRisk.write('\n')
        fRisk.write('-'*177)

        fRisk.write('<b>')
        fRisk.write(f'\n\nMargin Risk Chart: % Account NLV (*current risk level <=)\n')
        fRisk.write('</b>')
        fRisk.write('-'*81)
        fRisk.write('\n')
        fRisk.write(f'| 20% <= | ${netLiquidationValue*.20:>15.2f} | Margin Call at {((netLiquidationValue-(netLiquidationValue*.20))/netLiquidationValue)*100:.2f}% Drop | {"Low Risk":<16s} | {"<b><font color=""green"">*</font></b>" if (totalCashValuePerAccount*-1 <= netLiquidationValue*.20) else " "} |\n')
        fRisk.write(f'| 30% <= | ${netLiquidationValue*.30:>15.2f} | Margin Call at {((netLiquidationValue-(netLiquidationValue*.30))/netLiquidationValue)*100:.2f}% Drop | {"Medium Risk":<16s} | {"<b><font color=""orange"">*</font></b>" if (totalCashValuePerAccount*-1 <= netLiquidationValue*.30) and (totalCashValuePerAccount*-1 > netLiquidationValue*.20) else " "} |\n')
        fRisk.write(f'| 35% <= | ${netLiquidationValue*.35:>15.2f} | Margin Call at {((netLiquidationValue-(netLiquidationValue*.35))/netLiquidationValue)*100:.2f}% Drop | {"Mediam High Risk":<16s} | {"<b><font color=""orange"">*</font></b>" if (totalCashValuePerAccount*-1 <= netLiquidationValue*.35) and (totalCashValuePerAccount*-1 > netLiquidationValue*.30) else " "} |\n')
        fRisk.write(f'| 40% <= | ${netLiquidationValue*.40:>15.2f} | Margin Call at {((netLiquidationValue-(netLiquidationValue*.40))/netLiquidationValue)*100:.2f}% Drop | {"High Risk":<16s} | {"<b><font color=""red"">*</font></b>" if (totalCashValuePerAccount*-1 <= netLiquidationValue*.40) and (totalCashValuePerAccount*-1 > netLiquidationValue*.35) else " "} |\n')
        fRisk.write(f'| 50% >= | ${netLiquidationValue*.50:>15.2f} | Margin Call at {((netLiquidationValue-(netLiquidationValue*.50))/netLiquidationValue)*100:.2f}% Drop | {"Extreme Risk":<16s} | {"<b><font color=""red"">*</font></b>" if (totalCashValuePerAccount*-1 > netLiquidationValue*.40) else " "} |\n')
        fRisk.write('-'*81)

        fRisk.write('</pre> </body> </html>')
        # columnDataRisk.append(accountName)
        columnDataRisk.append([accountName,{'Margin':totalCashValuePerAccount},{'Net Liquidation Value':netLiquidationValue},{'Excess Liquidity':excessLiquidity},{'SMA':sma},{'Margin Cushion':marginCus},{'Margin %':marginPer}])
        fRisk.close()

    grandTotalMarginCus = ((grandTotalExcessLiquidity/grandTotalNetLiquidationVal) * 100)
    grandTotalMarginPer = (((grandTotalMarginBalance * -1)/grandTotalNetLiquidationVal) * 100)
    
    grandTotalNetLiquidationValCol="green" if (grandTotalNetLiquidationVal >= 0) else "red"
    grandTotalMarginBalanceCol="red" if (grandTotalMarginBalance < 0) else "green"
    grandTotalMarginCusCol = "green" if (grandTotalMarginCus >= 50) else "red"
    grandTotalMarginPerCol = "green" if (grandTotalMarginPer <= 12) else "red"
    f.write('\n\n<b>')
    f.write(f'{"Grand Total Net Liquidation Value: $":>36s} <font color="{grandTotalNetLiquidationValCol}">{grandTotalNetLiquidationVal:>15.2f}</font>')
    f.write('\n')
    f.write(f'{"Grand Total Margin Balance: $":>36s} <font color="{grandTotalMarginBalanceCol}">{grandTotalMarginBalance:>15.2f}</font>')
    f.write('\n\n')
    f.write(f'{"Grand Total Margin Cushion:  ":>36s} <font color="{grandTotalMarginCusCol}">{grandTotalMarginCus:>14.2f}%</font>')
    f.write('\n')
    f.write(f'{"Grand Total Margin Percent NLV:  ":>36s} <font color="{grandTotalMarginPerCol}">{grandTotalMarginPer:>14.2f}%</font>')
    f.write('\n')
    f.write(f'\nMargin Risk Chart: % Grand Total NLV (*current risk level <=)\n')
    f.write('</b>')
    f.write('-'*81)
    f.write('\n')
    f.write(f'| 20% <= | ${grandTotalNetLiquidationVal*.20:>15.2f} | Margin Call at {((grandTotalNetLiquidationVal-(grandTotalNetLiquidationVal*.20))/grandTotalNetLiquidationVal)*100:.2f}% Drop | {"Low Risk":<16s} | {"<b><font color=""green"">*</font></b>" if (grandTotalMarginBalance*-1 <= grandTotalNetLiquidationVal*.20) else " "} |\n')
    f.write(f'| 30% <= | ${grandTotalNetLiquidationVal*.30:>15.2f} | Margin Call at {((grandTotalNetLiquidationVal-(grandTotalNetLiquidationVal*.30))/grandTotalNetLiquidationVal)*100:.2f}% Drop | {"Medium Risk":<16s} | {"<b><font color=""orange"">*</font></b>" if (grandTotalMarginBalance*-1 <= grandTotalNetLiquidationVal*.30) and (grandTotalMarginBalance*-1 > grandTotalNetLiquidationVal*.20) else " "} |\n')
    f.write(f'| 35% <= | ${grandTotalNetLiquidationVal*.35:>15.2f} | Margin Call at {((grandTotalNetLiquidationVal-(grandTotalNetLiquidationVal*.35))/grandTotalNetLiquidationVal)*100:.2f}% Drop | {"Mediam High Risk":<16s} | {"<b><font color=""orange"">*</font></b>" if (grandTotalMarginBalance*-1 <= grandTotalNetLiquidationVal*.35) and (grandTotalMarginBalance*-1 > grandTotalNetLiquidationVal*.30) else " "} |\n')
    f.write(f'| 40% <= | ${grandTotalNetLiquidationVal*.40:>15.2f} | Margin Call at {((grandTotalNetLiquidationVal-(grandTotalNetLiquidationVal*.40))/grandTotalNetLiquidationVal)*100:.2f}% Drop | {"High Risk":<16s} | {"<b><font color=""red"">*</font></b>" if (grandTotalMarginBalance*-1 <= grandTotalNetLiquidationVal*.40) and (grandTotalMarginBalance*-1 > grandTotalNetLiquidationVal*.35) else " "} |\n')
    f.write(f'| 50% >= | ${grandTotalNetLiquidationVal*.50:>15.2f} | Margin Call at {((grandTotalNetLiquidationVal-(grandTotalNetLiquidationVal*.50))/grandTotalNetLiquidationVal)*100:.2f}% Drop | {"Extreme Risk":<16s} | {"<b><font color=""red"">*</font></b>" if (grandTotalMarginBalance*-1 > grandTotalNetLiquidationVal*.40) else " "} |\n')
    f.write('-'*81)
    f.write('<br><br><hr>')

    wr.writerow(columnDataRisk)
    wr.writerow('')
    f.write('<h3>Current Positions</h3>')
    grandTotalUPL = 0; grandTotalPL = 0
    wr.writerow(['POSITIONS'])
    for i in range(len(data)):
        accountId=data[i]['id']
        responsePos = requests.get('https://{IBeam}:5000//v1/api/portfolio/{accountId}/positions/'.format(accountId=accountId, IBeam=IBeam), verify=False)
        if responsePos.status_code != 200: print(f'({today}) Connection to IBKR API for Current Positions did not return 200, retrying in {sleepTimeSeconds} seconds..', file=sys.stderr); return
        accountName=data[i]['accountAlias']
        columnDataPos.append(accountName)
        filenamePos=accountName.replace(" ","-")
        accountId='************'+accountId[-2:]
        f.write(f'<h4>Account Name: {accountName}, Account ID: {accountId}</h4>')
        f.write(f'<a href="./Pos-{filenamePos}.html">{accountName}</a>\n')
        fPos = open(f"/usr/src/app/webserver/static/Pos-{filenamePos}_temp.html", "w+"); fileList.append(f"/usr/src/app/webserver/static/Pos-{filenamePos}_temp.html")
        fPosBuf = open(f"/usr/src/app/webserver/static/PosBuf-{filenamePos}.html", "w+")
        fPos.write(f'<html> <head> <title>{webPageTitle}: Current Positions: {accountName}</title> <link rel="shortcut icon" href="./favicon.ico"> <meta http-equiv="refresh" content="{refreshPageSeconds}"\/> </head> <body>')
        fPos.write('<pre>')
        fPos.write(f'<h4>Current Positions | Account Name: {accountName}, Account ID: {accountId} | Last Updated: {today}</h4>')
        fPos.write('<a href="./">Dashboard</a>\n\n')
        dataPos=responsePos.json()
        perAccountUPL = 0; perAccountPL = 0
        for i in range(len(dataPos)):
            contractDes=dataPos[i]['contractDesc']
            position=dataPos[i]['position']
            strike=dataPos[i]['strike']
            putOrCall=dataPos[i]['putOrCall']
            positionVal=dataPos[i]['mktValue']
            marketPrice=dataPos[i]['mktPrice']
            unrealizedPnL=dataPos[i]['unrealizedPnl']
            realizedPnL=dataPos[i]['realizedPnl']
            assetClass=dataPos[i]['assetClass']
            contractID=dataPos[i]['conid']
            grandTotalUPL+=unrealizedPnL
            grandTotalPL+=realizedPnL
            perAccountUPL+=unrealizedPnL
            perAccountPL+=realizedPnL
            
            if putOrCall == "C":
                putOrCallCol="green"; putOrCall="Call"
            elif putOrCall == "P":
                putOrCallCol="red"; putOrCall="Put"
            else:
                putOrCallCol="orange"
            
            if marketPrice > strike:
                strikeCol = "green"
            elif marketPrice < strike:
                strikeCol = "red"
            else:
                strikeCol = "orange"

            assetClassCol = "DarkGreen" if (assetClass == "STK") else "DarkOrange"

            positionValCol = "green" if (positionVal >= 0) else "red"
            UPnLCol = "green" if (unrealizedPnL >= 0) else "red"
            PnLCol = "green" if (realizedPnL >= 0) else "red"
            f.write('-'*318)
            f.write('\n')
            f.write(f'| {"Contract: ":<10s}{contractDes:<45s} | {"Position: ":<10s}{position:>12.5f} | {"Put/Call: ":<8s} <font color="{putOrCallCol}">{putOrCall}</font> | {"Strike: $":<9s} <font color="{strikeCol}">{strike:>12.2f}</font> | {"Market Price: $":<17s}{marketPrice:>15.2f} | {"Market Value: $":<17s} <font color="{positionValCol}">{positionVal:>15.2f}</font> | {"Unrealized PnL: $":<17s} <font color="{UPnLCol}">{unrealizedPnL:>15.2f}</font> | {"Realized PnL: $":<17s} <font color="{PnLCol}">{realizedPnL:>15.2f}</font> | {"Asset Class: ":<12s} <font color="{assetClassCol}">{assetClass:>5s}</font> | {"Contract ID: ":<13s}{contractID:<10d} |')
            f.write('\n')
            fPosBuf.write('-'*318)
            fPosBuf.write('\n')
            fPosBuf.write(f'| {"Contract: ":<10s}{contractDes:<45s} | {"Position: ":<10s}{position:>12.5f} | {"Put/Call: ":<8s} <font color="{putOrCallCol}">{putOrCall}</font> | {"Strike: $":<9s} <font color="{strikeCol}">{strike:>12.2f}</font> | {"Market Price: $":<17s}{marketPrice:>15.2f} | {"Market Value: $":<17s} <font color="{positionValCol}">{positionVal:>15.2f}</font> | {"Unrealized PnL: $":<17s} <font color="{UPnLCol}">{unrealizedPnL:>15.2f}</font> | {"Realized PnL: $":<17s} <font color="{PnLCol}">{realizedPnL:>15.2f}</font> | {"Asset Class: ":<12s} <font color="{assetClassCol}">{assetClass:>5s}</font> | {"Contract ID: ":<13s}{contractID:<10d} |')
            fPosBuf.write('\n')
            columnDataPos.append(f"ConDes:{contractDes},Pos:{position},MktVal:{positionVal},AsstCls:{assetClass},Strk:{strike},PutCall:{putOrCall},UnRlPnL:{unrealizedPnL},ConId:{contractID}") 
        f.write('-'*318)
        fPosBuf.write('-'*318)
        wr.writerow(columnDataPos)
        # wr.writerow('')
        columnDataPos.clear()
        fPosBuf.close()
        unrealizedPnLCol="green" if (perAccountUPL >= 0) else "red"
        realizedPnLCol="green" if (perAccountPL >= 0) else "red"
        fPos.write("<b>")
        fPos.write(f'{"Account Unrealized PnL: $":>25s} <font color="{unrealizedPnLCol}">{perAccountUPL:>15.2f}</font>')
        fPos.write("\n")
        fPos.write(f'{"Account Realized PnL: $":>25s} <font color="{realizedPnLCol}">{perAccountPL:>15.2f}</font>')
        fPos.write("</b>\n\n")
        with open(f"/usr/src/app/webserver/static/PosBuf-{filenamePos}.html", "r") as fPosBufRead: contents = fPosBufRead.readlines()
        contents = "".join(contents)
        fPos.write(contents)
        fPos.write("\n</pre> </body> </html>")
        fPos.close()

    grandTotalUPLCol="green" if (grandTotalUPL >= 0) else "red"
    grandTotalPLCol="green" if (grandTotalPL >= 0) else "red"
    f.write("\n\n<b>")
    f.write(f'{"Grand Total Unrealized PnL: $":>29s} <font color="{grandTotalUPLCol}">{grandTotalUPL:>15.2f}</font>')
    f.write("\n")
    f.write(f'{"Grand Total Realized PnL: $":>29s} <font color="{grandTotalPLCol}">{grandTotalPL:>15.2f}</font>')
    f.write("</b><br><br><hr>")
    # f.write('\n<a href="./IBKR_Data.csv">[Download CSV Data]</a>')
    f.write(f'<center><small>Last Updated: {today} | Parser Re-run Interval: {sleepTimeSeconds} seconds | Page Auto Refresh Interval: {refreshPageSeconds} seconds | System Uptime: {uptime} minutes | System Usage: {systemUsage} | <a href="./{csvFileName}.csv">[Download CSV Data]</a> | <a href="https://www.interactivebrokers.com/en/software/systemStatus.php" target="_blank" rel="noopener noreferrer">[System Status]</a></small></center>')
    f.write("\n</pre> </body> </html>")
    f.close()
    wr.writerow('')
    wr.writerow([f"Last Updated: {today}"])
    columnDataCsv.close()
    print(f'({today}) Web files creation completed')

    # write column data to csv file
    # with open("/usr/src/app/webserver/static/IBKR_Data_temp.csv", "w", newline='') as columnDataCsv:
    #     wr = csv.writer(columnDataCsv, quoting=csv.QUOTE_ALL)
    #     wr.writerow(columnDataRisk)
    #     wr.writerow(columnDataPos)
    #     wr.writerow('')
    #     wr.writerow([f"Last Updated: {today}"])
    fileList.append(f"/usr/src/app/webserver/static/{csvFileName}_temp.csv")

    # rename all temp webpage files for URL referencing including default index.html
    for source in fileList:
        dest=source.replace('_temp','')
        os.rename(source, dest)
    
    return

# call function every set number of seconds
# while True:
#     today=datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%B %d, %Y %I:%M%p %Z")
#     parseAPICreateWebFiles(today)
#     print(f'({today}) sleep time interval set to {sleepTimeSeconds}')
#     time.sleep(sleepTimeSeconds)

    # for i in range(sleepTimeSeconds,0,-1):
    #     print(f'Sleeping for {sleepTimeSeconds} seconds.. Press CTRL+C to end: {i:<10d}', end="\r")
    #     time.sleep(1)

if __name__ == '__main__':
    today=datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%B %d, %Y %I:%M%p %Z")
    parseAPICreateWebFiles(today)