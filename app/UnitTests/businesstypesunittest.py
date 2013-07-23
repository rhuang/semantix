import os
from os import listdir
import sys
import collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
from parsers import jsonparser as JsonParser
from parsers import businesstypeparser as BusinessTypeParser
from naivebayesclassifier.naivebayesclassifier import NaiveBayesClassifier

WINDOWS = 'nt'
reload(sys)
sys.setdefaultencoding('utf-8')

# Skipped
# clancysync
# empirepurveyors
# jeji, dragan file, did not download
# marchrestaurant
# ray bari

businessClassification = {
	"alexandregallery_com.txt" : "museum_gallery",
	"arjmed_com.txt" : "medical",
	"baumstevens_com.txt" : "legal",
	"beekmanschool_org.txt" : "education",
	"colliersabr_com.txt" : "financial_institutions",
	"constantin_com.txt" : "legal",
	"cpk_com.txt" : "restaurant",
	"dalvabrothers_com.txt" : "furniture",
	"dorothydraper_com.txt" : "furniture",
	"drsboyd_com.txt" : "medical",
	"escada_com.txt" : "apparel",
	"firstavenuevintner_com.txt" : "liquor",
	"genesisny_net.txt" : "financial_institutions",
	"informfitness_com.txt" : "health_beauty_personal",
	"jrobertscott_com.txt" : "furniture",
	"lamediterraneeny_com.txt" : "restaurant",
	"leperigord_com.txt" : "restaurant",
	"mckinneyrogers_com.txt" : "financial_institutions",
	"newel_com.txt" : "furniture",
	"nycdentist_com.txt" : "medical",
	"ojgallery_com.txt" : "museum_gallery",
	"orensteinlaw_com.txt" : "legal",
	"papillonbistro_com.txt" : "restaurant",
	"rischgroup_com.txt" : "legal",
	"rmany_com.txt" : "medical",
	"ronsafkodc_com.txt" : "medical",
	"rudinchiropractic_com.txt" : "medical",
	"vijaykbattumdpc_com.txt" : "medical",
	"scullyandscully_com.txt" : "furniture",
	"sleepys_com.txt" : "furniture",
	"sushiann_com.txt" : "restaurant",
	"suttonplacedentist_com.txt" : "medical",
	"suttonwine_com.txt" : "liquor",
	"suttonwines_com.txt" : "liquor"
}

def parseBusinessType(inputFile):
    nbc = NaiveBayesClassifier(os.path.join(settings.APP_DATA_TRAINING, 'businesses'))
    
    if inputFile.endswith('.txt'):
        jsonParsedTuple = JsonParser.parseData(inputFile, True)
        businessTuple = collections.namedtuple('Business', ['name', 'file', 'type'])

        businessTuple.name = jsonParsedTuple.name
        businessTuple.file = inputFile
        businessTuple.type = BusinessTypeParser.parse(inputFile, jsonParsedTuple.soups, nbc)
        return businessTuple


def verifyBusinessTypes():	
	for businessSite in businessClassification:
		business = parseBusinessType(os.path.join(settings.APP_DATA_HTML, businessSite))

		if business.type.label != businessClassification[businessSite]:
			print "\n", "ERROR!!"
			print businessSite, " classified as ", business.type.label
			print businessSite, " should be ", businessClassification[businessSite], "\n"
		else:
			print businessSite, " classified as ", business.type.label, " correctly "

print "STARTING BUSINESS TYPE UNIT TEST"
verifyBusinessTypes()
print "UNIT TEST COMPLETED"























