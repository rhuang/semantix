require 'stuff-classifier'

cls = StuffClassifier::Bayes.new("Location or Menu")

cls.train(:location, "1328 Stoneridge Mall Road, Pleasanton, CA, United States")
cls.train(:location, "49 West Maryland Street #104, Indianapolis, IN, United States")
cls.train(:location, "180 El Camino Real, Palo Alto, CA 94304, USA")
cls.train(:location, "100 Feet Rd, Indira Nagar, Bangalore, Karnataka 560038, India")
cls.train(:location, "Senapati Bapat Marg, Lower Parel, Mumbai, Maharashtra 400013, India")
cls.train(:location, "148 A, Weber Street North, Waterloo, Ontario, Canada")
cls.train(:location, "200 University Ave West, Waterloo, Ontario, Canada")
cls.train(:location, "2050 Royal Drive")
cls.train(:menu, "Quinoa (keen-wah) + Arugula Salad")
cls.train(:menu, "Cedar Plank Salmon + Corn Succotash")
cls.train(:menu, "Strawberry Shortcake")
cls.train(:menu, "Strawberry Mojito")
cls.train(:menu, "Habanero Carnitas Pizza")
cls.train(:menu, "Tacos + Sandwiches")
cls.train(:menu, "Steak Tacos")
cls.train(:menu, "Buffalo Chicken Wrap")
cls.train(:menu, "Baked Fish with potatoes")


@item = "75 Hazel glen place, waterloo, ontario"
print @item
print "\n"
print cls.classify(@item)
print "\n"



