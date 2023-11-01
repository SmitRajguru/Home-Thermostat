import pickle
from matplotlib import pyplot as plt

import numpy as np


def convertC2F(temprature):
    return temprature * 9 / 5 + 32


def convertF2C(temprature):
    return (temprature - 32) * 5 / 9


def getHeatIndex(temprature, humidity, isConvert=False):
    if isConvert:
        temprature = convertC2F(temprature)

    HI = []
    constList = [
        [
            -42.379,
            2.04901523,
            10.14333127,
            -0.22475541,
            -6.83783e-03,
            -5.481717e-02,
            1.22874e-03,
            8.5282e-04,
            -1.99e-06,
        ],
        [
            0.363445176,
            0.988622465,
            4.777114035,
            -0.114037667,
            -0.000850208,
            -0.020716198,
            0.000687678,
            0.000274954,
            0,
        ],
        [
            16.923,
            0.185212,
            5.37941,
            -0.100254,
            0.00941695,
            0.00728898,
            0.000345372,
            -0.000814971,
            0.0000102102,
            -0.000038646,
            0.0000291583,
            0.00000142721,
            0.000000197483,
            -0.0000000218429,
            0.000000000843296,
            -0.0000000000481975,
        ],
    ]
    for const in constList:
        k = int(len(const) ** 0.5) - 1
        const = np.array(const)

        T = []
        R = []
        for i in range(k + 1):
            T.append(temprature**i)
            R.append(humidity**i)

        T = np.array(T).reshape((k + 1, 1))
        R = np.array(R).reshape((k + 1, 1))

        coef = R @ T.T

        order = []
        for sub in range(k + 1):
            for itr in range(sub + 1):
                order.append((itr, sub))
                if itr != sub:
                    order.append((sub, itr))

        coefFlat = []
        for oElem in order:
            coefFlat.append(coef[oElem[0]][oElem[1]])
        coefFlat = np.array(coefFlat)

        newTemp = coefFlat @ const
        if isConvert:
            newTemp = convertF2C(newTemp)
        HI.append(newTemp)
    return HI


def plotData(data):
    time = []
    temprature = []
    humidity = []
    index = []

    for dt in data:
        time.append(dt[0])
        temprature.append(dt[1])
        humidity.append(dt[2])
        index.append(getHeatIndex(temprature[-1], humidity[-1], True))

    leg = ["Temprature (*C)", "Humidity (%)"]
    plt.plot(time, temprature)
    plt.plot(time, humidity)
    for itr in range(len(index[0])):
        plt.plot(time, [elem[itr] for elem in index])
        leg.append(f"Heat Index {itr}")
    plt.xlabel("Time")
    plt.legend(leg, loc="upper right")
    fig.canvas.draw()
    fig.canvas.flush_events()

    plt.show()


# plt.ion()
fig = plt.figure()

if __name__ == "__main__":
    mod = "examweek"

    with open(f"data/DHT_Data_{mod}.pickle", "rb") as file:
        data = pickle.load(file)

    plotData(data)

    input("Press any key to exit...")
