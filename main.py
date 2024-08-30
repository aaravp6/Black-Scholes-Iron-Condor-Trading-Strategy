print('program started...')

import datetime
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import BlackScholesModel
import math
import matplotlib.pyplot as plt

start = datetime.datetime(1982, 4, 20)
end = datetime.datetime(2021, 3, 23)

dfSPY = web.DataReader('^GSPC', 'yahoo', start, end)


#print(dfSPY)
print('trying to graph')

x = np.linspace(0, 20, 100)  # Create a list of evenly-spaced numbers over the range
plt.plot(x, np.sin(x))       # Plot the sine of each x point
plt.show()                   # Display the plot

#print(BlackScholesModel.orgDataReturns(dfSPY, '1982-04-28'))
print(BlackScholesModel.getCall(dfSPY, '2021-03-18', '2021-03-22', 3810))

myPercentChangeThresholdLow = -0.03
myPercentChangeThresholdHigh = 0.03
myDayRange = 3

def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date

def myAddBusinessDays(date, days):
    curDate = datetime.datetime.strptime(date, '%Y-%m-%d')
    newDate = date_by_adding_business_days(curDate, days)
    return str(newDate).split()[0]

def functionToOptions(function, expiration):
    options = []
    #the function will take on the following characteristic
    #[(strikePrice, slope), (strikePrice, slope) ..., (strikePrice, slope)]
    #if strike price is None, then on left side
    #first 2 strike prices repeat
    #first node is put
    index = 0
    for node in function:
        nodeStrikePrice = node[0]
        nodeSlope = node[1]
        if index == 0:
            print('0')
            options.append([nodeSlope, 'put', expiration, nodeStrikePrice])
        elif index == 1:
            print('1)')
            options.append([nodeSlope, 'call', expiration, nodeStrikePrice])
        else:
            print('2')
            prevNodeSlope = function[index - 1][1]
            options.append([nodeSlope - prevNodeSlope, 'call', expiration, nodeStrikePrice])
        index += 1
    return options


def optionsValue(SPYPrice, curDate, options):
    #the value of a function is also the cost to close it
    #cost to close can be negative, which shows person will get money to close this
    #each function in functions will be tuple with 3 characteristics: [contractAmount, putOrCall, expiration, strike price]
    costToOpen = 0
    for options in options:
        contractAmount, putOrCall, daysToExpiration, strikePrice = options[0], options[1], options[2], options[3]
        print(curDate)
        #print('addbusiness days', myAddBusinessDays(curDate, daysToExpiration))
        if putOrCall == 'call':
            costToOpen += contractAmount*BlackScholesModel.getCall(dfSPY, curDate, myAddBusinessDays(curDate, daysToExpiration), strikePrice)
        elif putOrCall == 'put':
            costToOpen += contractAmount*BlackScholesModel.getPut(dfSPY, curDate, myAddBusinessDays(curDate, daysToExpiration), strikePrice)
        else:
            print('invalid option type')
        print('hi')
    return costToOpen

def graphFunction(function, SPYPrice, curDate, daysToExpiration):
    options = functionToOptions(function, daysToExpiration)
    costToOpen = optionsValue(SPYPrice, curDate, options)
    notablePoints = []
    strikeRange = function[-1][0] - function[0][0]

    nodenum = 1
    currentProfit = costToOpen
    for node in function[1:]:
        nodeStrikePrice = node[0]
        nodeSlope = node[1]
        prevNode = function[nodenum-1]
        prevNodeStrikePrice = prevNode[0]
        prevNodeSlope = prevNode[1]

        if nodenum == 1:
            notablePoints.append([nodeStrikePrice, currentProfit])
        elif False:
            pass
        else:
            currentProfit += prevNodeSlope*(nodeStrikePrice-prevNodeStrikePrice)
            notablePoints.append([nodeStrikePrice, currentProfit])

        nodenum+=1
    #for the extra point on right side
    extraPointDist = strikeRange/4
    notablePoints.append([function[-1][0] + extraPointDist, notablePoints[-1][1] + extraPointDist*function[-1][1]])
    #extra point on left
    notablePoints.insert(0, [function[0][0] - extraPointDist, notablePoints[0][1] - extraPointDist*function[0][1]])

    #convert the notable points into 2 lists
    convertedNotablePoints = [[point[0] for point in notablePoints], [point[1] for point in notablePoints]]
    print(notablePoints)
    print('\n\n\n')
    plt.plot(convertedNotablePoints[0], convertedNotablePoints[1], '-bo')
    plt.show()


print(functionToOptions([[300, -1], [300, 0], [400, 2], [500, 1]], 5))
myFunction = [[350, 0], [350, 1], [390, -1], [440, 0]]
myOptions = functionToOptions([[350, 0], [350, 1], [390, -1], [430, 0]], 5)
graphFunction(myFunction, 4000, '2021-03-18', 5)
print('cost to open', optionsValue(390, '2021-03-18', myOptions))

def getPerformance(percentChangeThresholdLow, percentChangeThresholdHigh, dayRange):
    aboveThresholdCount = 0
    curNetVal = 0

    lcp = 3915.4599609375
    print('business', myAddBusinessDays('2021-03-18', 2))

    #puts are behaving wierdly
    longPutVal = BlackScholesModel.getPut(dfSPY, '2021-03-15', myAddBusinessDays('2021-03-15', dayRange), math.floor(lcp*(1+percentChangeThresholdLow)/10)*10)
    print('longPutVal', longPutVal)
    shortPutVal = BlackScholesModel.getPut(dfSPY, '2021-03-15', myAddBusinessDays('2021-03-15', dayRange), math.ceil(lcp*(1+percentChangeThresholdLow)/10)*10)
    print('shortPutVal', shortPutVal)
    shortCallVal = BlackScholesModel.getCall(dfSPY, '2021-03-15', myAddBusinessDays('2021-03-15', dayRange), math.floor(lcp*(1+percentChangeThresholdHigh)/10)*10)
    print('shortCallVal', shortCallVal)
    longCallVal = BlackScholesModel.getCall(dfSPY, '2021-03-15', myAddBusinessDays('2021-03-15', dayRange), math.ceil(lcp*(1+percentChangeThresholdHigh)/10)*10)
    print('longCallVal', longCallVal)
    print(BlackScholesModel.getPut(dfSPY, '2021-03-15', myAddBusinessDays('2021-03-15', dayRange), 5000))

    credit = (shortPutVal + shortCallVal - longPutVal - longCallVal)*10
    print(longPutVal, shortPutVal, shortCallVal, longCallVal)
    print('credit', credit)

    for index,row in dfSPY.head(len(dfSPY) - dayRange + 1).iterrows():
        #index = str(index).split()[0]
        #print(index)

        #print('\nDay', index)

        high = row['High']
        low = row['Low']
        open = row['Open']
        close = row['Close']

        for dayNum in range(dayRange):
            #curDate = datetime.datetime.strptime(str(index), '%Y-%m-%d')
            #i = curDate.replace(day=curDate.day + dayNum)
            i = np.where(dfSPY.index == index)[0][0] + dayNum
            #print(i, 'i')
            thisRow = dfSPY.iloc[i]
            if thisRow['High'] > high:
                high = thisRow['High']
            if thisRow['Low'] > low:
                low = thisRow['Low']

        percentChangeLow = low/open - 1
        percentChangeHigh = high/open - 1

        #print('business', myAddBusinessDays('2021-03-18', 2))



        if percentChangeLow < percentChangeThresholdLow or percentChangeHigh > percentChangeThresholdHigh:
            aboveThresholdCount += 1
            curNetVal += - 50
        else:
            curNetVal += credit




    print('threshold(s) passed ',aboveThresholdCount, 'out of around 10140 trading days')
    print('accuracy:', 1 - aboveThresholdCount/10140)
    print(curNetVal/10140, 'average dollars gained per day')

getPerformance(myPercentChangeThresholdLow, myPercentChangeThresholdHigh, myDayRange)
print('program ended...')