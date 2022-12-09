#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm
import warnings
warnings.filterwarnings("ignore")

def operating_systems_collection():
    # standardize column name to "OpSys"
    OpSysDict = {"Percent":{}} #example {'windows' : {2022 : 23000, 2021 : 98}}
    for i in range(2022, 2010, -1):
        if i == 2015:
            df = pd.read_csv("survey_results_2015.csv", encoding="latin", header=1) # This csv is formatted differently than the others
        else:
            df = pd.read_csv(f'survey_results_{i}.csv', encoding="latin")
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #this removes unnamed columns from a dataframe, i got it from stack overflow
        wanted_column = ""
        for col in df.columns:
            if ('Windows' in df[col].unique() or 'macOS' in df[col].unique() or 'Linux' in df[col].unique() or 'Ubuntu' in df[col].unique()) and not 'iOS' in df[col].unique() and not 'Unix' in df[col].unique():
                #print(col) # for debug purposes
                wanted_column = col
                break
        else: # This else is part of the for loop, it runs when the for loop exits without the break being called
            continue
        df.rename(columns = { wanted_column : "OpSys" }, inplace = True)
        df = df.loc[:,"OpSys"]

        # TODO: ask Mr. Moden if this can be vectorized. I don't think so because some values have semicolons and some don't and they need to be handled differently
        #assembling the dictionary
        numNotRespond = 0
        for j in df:
            if isinstance(j, float):
                numNotRespond += 1
                continue
            for k in j.split(";"):
                if k in OpSysDict:
                    Kdict = OpSysDict[k]
                    if i in OpSysDict[k]:
                        Kdict[i] += 1
                    else:
                        Kdict[i] = 1
                else:
                    OpSysDict[k] = {i:1}
        OpSysDict["Percent"][i] = 1 - (float(numNotRespond) / float(len(df)))
        print(i)
    dataframe = pd.DataFrame.from_dict(OpSysDict)

    #manipulate dataframe (add year column title, delete response column, combine 'other' and 'BSD' and 'macOS' columns, make cumul columns)
    dataframe.set_index(dataframe.iloc[:,0])
    dataframe.index.name = "Year"
    del dataframe["Response"]
    dataframe[np.isnan(dataframe)] = 0
    dataframe["BSD"] = dataframe["BSD"] + dataframe["BSD/Unix"]
    del dataframe["BSD/Unix"]
    dataframe["Other"] = dataframe["Other (please specify):"] + dataframe["Other"]
    del dataframe["Other (please specify):"]
    dataframe["macOS"] = dataframe["macOS"] + dataframe["MacOS"] + dataframe["Mac OS X"]
    del dataframe["MacOS"]
    del dataframe["Mac OS X"]
    dataframe["Total"] = dataframe.iloc[:,1:].sum(axis = 1)
    dataframe["cumulWindows"] = dataframe["Windows"] + dataframe["Windows 10"] + dataframe["Windows 8"] + dataframe["Windows 7"]  + dataframe["Windows XP"] + dataframe["Windows Vista"]
    dataframe["cumulLinux"] = dataframe["Linux-based"] + dataframe["Other Linux"]  + dataframe["Ubuntu"] + dataframe["Fedora"] + dataframe["Mint"] + dataframe["Debian"] + dataframe["Linux"] + dataframe["Windows Subsystem for Linux (WSL)"]

    #write dataframe to csv
    dataframe.to_csv("OpSys.csv")
    print("done collecting OpSys data")


def operating_systems_graphing():
    df = pd.read_csv("OpSys.csv", encoding="latin", index_col="Year")

    # turning the raw values of linux distros into percentages
    df["Windows Subsystem for Linux (WSL)"] = df["Windows Subsystem for Linux (WSL)"] / df["cumulLinux"]
    df["Linux-based"] = df["Linux-based"] / df["cumulLinux"]
    df["Other Linux"] = df["Other Linux"] / df["cumulLinux"]
    df["Ubuntu"] = df["Ubuntu"] / df["cumulLinux"]
    df["Fedora"] = df["Fedora"] / df["cumulLinux"]
    df["Mint"] = df["Mint"] / df["cumulLinux"]
    df["Debian"] = df["Debian"] / df["cumulLinux"]
    df["Linux"] = df["Linux"] / df["cumulLinux"]

    # turning the raw values into percentages
    df["macOS"] = df["macOS"] / df["Total"]
    df["cumulWindows"] = df["cumulWindows"] / df["Total"]
    df["cumulLinux"] = df["cumulLinux"] / df["Total"]
    df["BSD"] = df["BSD"] / df["Total"]
    df["Other"] = df["Other"] / df["Total"]

    # plot the operating systems
    fig, ax = plt.subplots(1, 2)
    generalOsPlot = sns.lineplot(data=df[["macOS", "cumulWindows", "cumulLinux", "BSD", "Other"]], ax=ax[0])
    generalOsPlot.set_ylabel("Percentage of Respondants")
    generalOsPlot.set_title("Percent of Respondants Who Use Each Operating System By Year", fontsize=9)
    linuxPlot = sns.lineplot(data=df[["Windows Subsystem for Linux (WSL)", "Linux-based", "Other Linux", "Ubuntu", "Fedora", "Mint", "Debian", "Linux"]], ax=ax[1])
    linuxPlot.set_title("Percent of Respondants Who Use Each Linux Distro By Year", fontsize=9)
    linuxPlot.set_ylabel("Percentage of Linux-using Respondants")
    sns.move_legend(generalOsPlot, "upper right")
    sns.move_legend(linuxPlot, "upper right")
    #sns.heatmap(data=df[["macOS", "cumulWindows", "cumulLinux", "BSD", "Other"]]) # for the sake of making a heatmap
    plt.show()

def languages_and_ages_collection():
    df = pd.read_csv("survey_results_2022.csv", encoding="latin", index_col="ResponseId")
    df = df.loc[:,["Age", "LanguageHaveWorkedWith"]]
    ageLangsDict = {} #example {'C++' : {25-34 years old : 23000, 55-64 years old : 98}} 
    for i in zip(df["Age"], df["LanguageHaveWorkedWith"]):
        if isinstance(i[1], float):
            i = (i[0], "NotRespond")
        if isinstance(i[0], float):
            i = ("NotRespond", i[1])
        for j in i[1].split(";"):
            if j in ageLangsDict:
                if i[0] in ageLangsDict[j]:
                    ageLangsDict[j][i[0]] += 1
                else:
                    ageLangsDict[j][i[0]] = 1
            else:
                ageLangsDict[j] = {i[0] : 1}
    dataframe = pd.DataFrame.from_dict(ageLangsDict)

    #manipulate dataframe (add age column title, combine NotRespond and Prefer Not to Say rows)
    dataframe.set_index(dataframe.iloc[:,0])
    dataframe.index.name = "Age"
    dataframe.loc["Prefer not to say", :] += dataframe.loc["NotRespond", :]
    dataframe.drop(["NotRespond"], inplace=True)

    dataframe.to_csv("AgesLangs.csv")
    print("done collecting AgeLang data")

def languages_and_ages_graphing():
    sns.set_theme(font_scale=.5)
    dataframe = pd.read_csv("AgesLangs.csv", encoding="latin", index_col="Age")
    dataframe = dataframe[["Swift", "Solidity", "TypeScript", "Elixir", "Julia", "Dart", "Crystal", "Kotlin", "Go", "Groovy", "Clojure", "PowerShell", "Rust", "Scala", "C#", "F#", "HTML/CSS", "OCaml", "Java", "Delphi", "JavaScript", "Ruby", "R", "PHP", "Lua", "VBA", "Python", "Haskell", "Bash/Shell", "Perl", "Erlang", "MATLAB", "C++", "Objective-C", "SAS", "C", "SQL", "APL", "LISP", "COBOL", "Fortran", "Assembly"]]
    dataframe = dataframe.loc[["Under 18 years old", "18-24 years old", "25-34 years old", "35-44 years old", "45-54 years old", "55-64 years old", "65 years or older"],:]
    #percentage of age group
    #I tried using the vectorized form for this and it did not work for some reason
    #I tried saying: dataframe /= dataframe.sum(axis=1)
    for i in range(dataframe.shape[0]):
        dataframe.iloc[i,:] = dataframe.iloc[i,:] / dataframe.iloc[i,:].sum()

    #percentage of language, although I don't think this is super useful
    """dataframe /= dataframe.sum()"""

    heatAx = sns.heatmap(data=dataframe)
    heatAx.set_title("Percentage of Each Age Group Who Use Each Language")
    plt.show()

def best_areas_graphing():
    sns.set_theme(font_scale=.5)
    dataframe = pd.read_csv("survey_results_2022.csv", encoding="latin", index_col="ResponseId")
    dataframe = dataframe[["Country", "ConvertedCompYearly"]]
    dataframe.dropna(axis="index", inplace=True)

    #filter out countries whose average is less than 200k and who have less than 10 datapoints
    countriesToEliminate = {}
    for i in range(dataframe.shape[0]):
        row = dataframe.iloc[i,:]
        if row[0] in countriesToEliminate:
            countriesToEliminate[row[0]][0] = (countriesToEliminate[row[0]][0] * countriesToEliminate[row[0]][1] + row[1]) / (countriesToEliminate[row[0]][1] + 1)
            countriesToEliminate[row[0]][1] += 1
        else:
            countriesToEliminate[row[0]] = [row[1], 1]
    items = list(countriesToEliminate.items())
    for k, v in items:
        if v[0] > 200_000 and v[1] > 10:
            del countriesToEliminate[k]
    countriesToEliminate = list(countriesToEliminate.keys())
    indexesToKeep = []
    for i in range(dataframe.shape[0]):
        if dataframe.iloc[i,0] not in countriesToEliminate:
            indexesToKeep.append(i)
    dataframe = dataframe.iloc[indexesToKeep,:]
    
    sns.boxplot(x="Country", y="ConvertedCompYearly", data=dataframe, showfliers=False)
    plt.xticks(rotation=90)
    plt.show()

def experience_and_salaries_graphing():
    dataframe = pd.read_csv("survey_results_2022.csv", encoding="latin", index_col="ResponseId")
    dataframe = dataframe[["YearsCode", "YearsCodePro", "WorkExp", "ConvertedCompYearly", "EdLevel", "LearnCode", "OrgSize", "OpSysProfessional use", "Gender", "Trans", "Sexuality"]]
    dataframe.dropna(axis="index", inplace=True)
    dataframe['YearsCode'] = dataframe['YearsCode'].replace(to_replace='Less than 1 year', value='1')
    dataframe['YearsCode'] = dataframe['YearsCode'].replace(to_replace='More than 50 years', value='51')
    dataframe['YearsCode'] = pd.to_numeric(dataframe['YearsCode'])

    plt.subplot(2, 2, 1)    
    print("graphing first")
    indivKDEax = sns.kdeplot(data=dataframe, x="YearsCode", y="ConvertedCompYearly")
    indivKDEax.set_ylim(top=1_000_000)
    plt.subplot(2, 2, 2)
    print("graphing second")
    sns.violinplot(data=dataframe, x="YearsCode")
    plt.subplot(2, 2, 3)
    print("graphing third")
    sns.regplot(data=dataframe, x="YearsCode", y="ConvertedCompYearly", scatter=False)
    print("graphing last")
    plt.subplot(2, 2, 4)
    KDEax = sns.kdeplot(data=dataframe, x="YearsCode", y="ConvertedCompYearly")
    sns.regplot(data=dataframe, x="YearsCode", y="ConvertedCompYearly", scatter=False)
    KDEax.set_ylim(0, 1_000_000)
    violinAx = sns.violinplot(data=dataframe, x="YearsCode", ax=KDEax.twinx())
    plt.xticks(rotation=90)
    #plt.setp(violinAx.collections, alpha=.3)
    plt.show()

def main():
    experience_and_salaries_graphing()
    #TODO: plot something that has three or more variables (meaning you involve hue/size) (mandatory)
    #continuous variables: YearsCode, YearsCodePro, CompTotal, WorkExp, ConvertedCompYearly
    #either choose around 6 languages to look at or group them somehow, maybe by decade or dynamically vs statically or object-oriented vs functional vs scripting?
    #TODO: maybe plot where people make the most money, like a category plot of box plots where the x axis is currencies and the y axis is convertedcompyearly, if not do this try to do a singular violin plot of something
    #TODO: maybe make a scatterplot or a linear regression plot of two continuous variables (and involve a third variable in the hue if a scatterplot!)

if __name__ == "__main__": 
    main()
