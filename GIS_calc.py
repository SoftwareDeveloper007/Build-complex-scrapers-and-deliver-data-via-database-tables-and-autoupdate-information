class GIS_calc():
    def __init__(self, gc, lat_lng):
        self.lat_lng = lat_lng
        self.gc = gc
        self.isTrue = False
        self.lat = []
        self.lng = []
        self.countries = []
        print(self.lat_lng)

    def parse(self):

        if self.lat_lng == "FishBase does not have latitudinal and longitudinal range for this ecosystem.":
            self.isTrue = False
        else:
            self.isTrue = True
            self.lat_lng = self.lat_lng.split(' ')
            if '-' in self.lat_lng:
                self.lat_lng.remove('-')
            print(self.lat_lng)

            for i in range(len(self.lat_lng)):
                if '°' in self.lat_lng[i]:
                    self.lat_lng[i] = self.lat_lng[i].replace("°", "")

            for j in [1, 3, 5, 7]:
                if self.lat_lng[j] is 'N' or self.lat_lng[j] is 'n':
                    self.lat_lng[j-1] = float(self.lat_lng[j-1])
                elif self.lat_lng[j] is 'S' or self.lat_lng[j] is 's':
                    self.lat_lng[j - 1] = - float(self.lat_lng[j - 1])
                elif self.lat_lng[j] is 'E' or self.lat_lng[j] is 'e':
                    self.lat_lng[j-1] = float(self.lat_lng[j-1])
                elif self.lat_lng[j] is 'W' or self.lat_lng[j] is 'w':
                    self.lat_lng[j - 1] = - float(self.lat_lng[j - 1])
            print(self.lat_lng)

            self.lat = [self.lat_lng[0], self.lat_lng[2]]
            self.lng = [self.lat_lng[4], self.lat_lng[6]]

            #print(self.lat)
            #print(self.lng)

            #self.reverse_gis()


    def reverse_gis(self):

        if self.isTrue:
            self.lat[0] = int(self.lat[0])
            self.lat[1] = int(self.lat[1])
            self.lng[0] = int(self.lng[0])
            self.lng[1] = int(self.lng[1])

            if self.lat[0]<self.lat[1]:
                self.lat_stp = 10
            else:
                self.lat_stp = -10
            if self.lng[0]<self.lng[1]:
                self.lng_stp = 10
            else:
                self.lng_stp = -10

            #countries = []
            for lat in range(self.lat[0], self.lat[1], self.lat_stp):
                for lng in range(self.lng[0], self.lng[1], self.lng_stp):
                    geocode = self.gc.geocode(lat, lng, max_dist=0)
                    if (geocode is not None) and (geocode['Sovereign1'] is not None):
                        if (geocode['Sovereign1'] not in self.countries):
                            self.countries.append(geocode['Sovereign1'])

        self.countries.extend(['-', '-', '-', '-', '-', '-',
                               '-', '-', '-', '-'])


        print(self.countries[0:10])





if __name__ == '__main__':
    app = GIS_calc('71° N 51° N - 82° e 105° e')
    app.parse()