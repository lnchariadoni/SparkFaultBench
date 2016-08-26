import mod_config
from randomUtils import RandomUtils
import random, time, math

#
GenType = "NORMAL"

#words
maxurllen = 100
minurllen = 10
maxwordlen = 10
minwordlen = 2
extractUrl = 30
#file
filemean = 10000
filevar = 1000
f1 = "rankings.txt"
f2 = "uservisits.txt"

#table
rankings_col = 10
userVisits_col = 100

#gen
urldict = {}
urls = []
params={}

#freq
link_fre = 0.05
#zipf
zipf = []
zipf_param = 0.5
num_bins = 0
'''
rankings (
    pageURL STRING,
    pageRank INT,
    avgDuration INT
)

uservisits (
    sourceIP STRING,
    destURL STRING,
    visitDate STRING,
    adRevenue DOUBLE,
    userAgent STRING,
    countryCode STRING,
    languageCode STRING,
    searchWord STRING,
    duration INT
)
'''


def getConfigPar():
    configs = mod_config.getConfigBySection('base','paramenter_conf')
    for item in configs:
        params[item[0]] = item[1]
    global rankings_col
    rankings_col = int(params['rankings_col'])
    global userVisits_col
    userVisits_col = int(params['uservisits_col'])


def genUrls():
    urlhead = "http://"
    urlend = ".html"
    for i in range(rankings_col):
        urllen = RandomUtils.randomInt(minurllen,maxurllen)
        urlname = RandomUtils.randomUrlname(urllen)
        strurl = urlhead + urlname + urlend
        urls.append(strurl)
        if (i % 10000 == 0):
            print "generated %d urls" % i
    for i in range(rankings_col):
        #genPageContent()
        genSimplePageContent()
        if (i % 1000 == 0):
            print "generated %d exctr url" % i


def getUrl():
    no = int((num_bins-1) * RandomUtils.randomBase())
    #print "no=%d zipf[no]=%d" %(no,zipf[no])
    return urls[zipf[no]]

def genSimplePageContent():
    for i in range (extractUrl):
        extUrl = getUrl()
        if extUrl in urldict.keys():
            urldict[extUrl] += 1
        else:
            urldict[extUrl] = 1

def genPageContent():
    totallen = 0
    filelen = int(filemean + filevar * RandomUtils.randomNormal())
    while 1:
        fl = RandomUtils.randomBase()
        if fl < link_fre:
            extUrl = getUrl()
            if extUrl in urldict.keys():
                urldict[extUrl] += 1
            else:
                urldict[extUrl] = 1
            contentlen = len(extUrl)
        else:
            contentlen = RandomUtils.randomInt(minwordlen,maxwordlen)
        totallen += contentlen
        if totallen >= filelen:
            break

def genIP():
    fst = RandomUtils.randomInt(0,223)
    snd = RandomUtils.randomInt(0,255)
    trd = RandomUtils.randomInt(0,255)
    fth = RandomUtils.randomInt(0,255)
    return str(fst)+'.'+str(snd)+'.'+str(trd)+'.'+str(fth)


def loadfile(filename):
    f = open('data_files/'+filename,'r')
    content=f.readlines()
    f.close()
    return content


def load_zipf():
    numurls = rankings_col
    sum = 0.0
    min_bucket = 0
    max_bucket = 0
    residual = 0.0
    global num_bins
    num_bins = rankings_col * 10

    for i in range(1,numurls+1):
        val = 1.0 / math.pow(i, zipf_param)
        sum += val
    for i in range(numurls):
        link_prob =  (1.0 / math.pow((i+1), zipf_param)) / sum
        max_bucket = int(min_bucket + num_bins * (link_prob + residual))
        for j in range(min_bucket,max_bucket):
            zipf.append(i)
        residual += link_prob - (float(max_bucket - min_bucket) / num_bins)

        if (residual < 0):
            residual = 0
        min_bucket = max_bucket


def getDestinationUrl():
    if GenType == 'NORMAL':
        return urls[RandomUtils.randomInt(0,len(urls)-1)]
    else:
        ra = RandomUtils.randomBase()
        if ra < 0.8:
            return urls[0]
        else:
            return urls[RandomUtils.randomInt(0,len(urls)-1)]


def genRankingsFile(outputfile):
    f = open(outputfile,'w')
    for key in urldict.keys():
        pagerank = urldict[key]
        pageurl = key
        avgDuration = RandomUtils.randomInt(1,100)
        content = str(pagerank)+','+pageurl+','+str(avgDuration)+"\n"
        f.write(content)
    f.close()


def genUservisitsFile(outputfile):
    output = open(outputfile,'w')
    agents = loadfile('user_agents.dat')
    codes = loadfile('country_codes_plus_languages.dat')
    keywords = loadfile('keywords.dat')

    for i in range(userVisits_col):
        sourceIP = genIP()
        destURL = getDestinationUrl()
        visitDate = RandomUtils.randomDate()
        adRevenue = RandomUtils.randomFloat(1000.0)
        userAgent = agents[RandomUtils.randomInt(0,len(agents)-1)].strip().replace(',', ' ')
        mycode = codes[RandomUtils.randomInt(0,len(codes)-1)].strip().split(',')
        countryCode = mycode[0]
        languageCode = mycode[1]
        searchWord = keywords[RandomUtils.randomInt(0,len(keywords)-1)].strip()
        duration = RandomUtils.randomInt(1,100)

        content = "%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (sourceIP, destURL,visitDate,adRevenue,userAgent,countryCode,languageCode,searchWord,duration)
        output.write(content)
    output.close()


def genOutputName():
    print "generate urls successfully"
    global f1,f2
    if (GenType == 'NORMAL'):
        f1 = "rankings.txt"
        f2 = "uservisits.txt"
    else:
        f1 = "rankings_skewed.txt"
        f2 = "uservisits_skewed.txt"

def run():
    getConfigPar()
    print "get config paramters successfully"
    load_zipf()
    print "load_zipf successfully"
    genUrls()
    genOutputName()
    genRankingsFile(f1)
    print "generate rankings table successfully"
    genUservisitsFile(f2)
    print "generate uservisits table successfully"

run()