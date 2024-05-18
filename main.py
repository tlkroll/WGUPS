import csv
import Hash
import datetime
import copy

package_table = Hash.ChainingHashTable() # creates an instance of the hash table function

with open('distances.csv') as csvfile: # opens distances as a table to be read for calculations
    distances = csv.reader(csvfile)   
    distances = list(distances) 
    
with open('packages.csv') as csvfile: # opens packages as a table
    destination = csv.reader(csvfile)
    destination = list(destination)
    for package in destination:
            p_id = int(package[0])
            address = package[1]
            city = package[2]
            p_zip = package[3]
            deadline = package[4]
            weight = package[5]
            note = package[6]
            truck = package[7]
            dist_index = int(package[8])
            status = package[9]

            p = (p_id, address, city, p_zip, deadline, weight, note, truck, dist_index, status)

            package_table.insert(p_id, p) # inserts package information into hash table
            
truck1load = {} # dictionaries to hold packages on individual trucks
truck2load = {}
truck3load = {}

priority_list = {} # temporary dictionary to hold priority packages while they are being delivered

timestamps = {} # dictionary to record timestamps of all packages each time a package is delivered

#truck  current location (distances row),       packages, mileage,                           time
truck1=[                               0,     truck1load,       0,    datetime.timedelta(hours=8)]
truck2=[                               0,     truck2load,       0,    datetime.timedelta(hours=8)]
truck3=[                               0,     truck3load,       0,    0] # truck 3 departs when driver is finished with truck 2

def load_trucks(): # loads packages into truckload dictionaries with package id as key and distance from current location as value
    for i in destination: 
        pID = int(i[0])
        pTruck = i[7]
        if pTruck == "1" and i[9] == "At the hub":
            truck1load[pID] = float(distances[int(i[8])][int(truck1[0])])
            i[9] = "Loaded on Truck 1"
            package_table.insert(pID, i)
        elif pTruck == "2" and i[9] == "At the hub":
            truck2load[pID] = float(distances[int(i[8])][int(truck2[0])])
            i[9] = "Loaded on Truck 2"
            package_table.insert(pID, i)
        elif pTruck == "3" and i[9] == "At the hub":
            truck3load[pID] = float(distances[int(i[8])][int(truck3[0])])
            i[9] = "Loaded on Truck 3"
            package_table.insert(pID, i)
   
def next_stop(truck, load): # this is the function which actually "delivers" the packages and updates all necessary information
    closest = min(load.values()) # selects lowest mileage stop from load
    key_list = list(load.keys())
    val_list = list(load.values())
    position = val_list.index(closest)# distance to next closest stop
    location = key_list[position]# package ID of next closest stop
    
    for i in load: # updates package distances with updated truck location
        row = int(destination[truck[0]-1][8])
        column = int(destination[i-1][8])
        if distances[row][column] == "":
            load[i] = float(distances[column][row])
        else:
            load[i] = float(distances[row][column])

    # delivery stop
    truck[3] = truck[3] + (datetime.timedelta(minutes=(closest * 3.333))) # updates time on truck
    destination[location - 1][9] = "delivered at " + str(truck[3]) #updates status on truck
    package_table.insert(location, destination[location - 1]) # updates hash table with new status
    
    timestamps[(truck[3])] = copy.deepcopy(destination) # creates a "snapshot" of all package statuses and stores them with the timestamp as a key

    truck[0] = location # updates truck's location to package just delivered
    truck[2] = truck[2] + closest # adds mileage from stop
    load.pop(location) # removes delivered package from truck load

def begin_deliveries():
    while len(truck1load) > 0: # makes stops for truck 1 - repeated for 2 and 3
        for i in truck1load:
            deadline = destination[i-1][4] # adds priority packages to priority_list
            if deadline != "EOD":
                priority_list[i] = float(distances[int(destination[i-1][8])][int(truck1[0])])
        for i in priority_list: 
            truck1load.pop(i) # removes packages from original load so they are not "delivered" twice
        while len(priority_list) > 0:
            next_stop(truck1, priority_list) # delivers packages from priority_list before starting the rest of the route
        next_stop(truck1, truck1load) # delivers packages with no deadline

    while len(truck2load) > 0:
        for i in truck2load:
            deadline = destination[i-1][4]
            if deadline != "EOD":
                priority_list[i] = float(distances[int(destination[i-1][8])][int(truck2[0])])
        for i in priority_list: 
            truck2load.pop(i)
        while len(priority_list) > 0:
            next_stop(truck2, priority_list)
        next_stop(truck2, truck2load)

    truck3[3] = truck2[3] # updates truck 3 time when driver from truck 2 leaves hub with truck 3 after final delivery
    
    destination[5][9] = "Loaded on Truck 3" # driver from truck 2 loads packages onto truck 3
    truck3load[6] = float(distances[int(destination[5][8])][0])
    package_table.insert(6, (destination[5]))
    
    destination[24][9] = "Loaded on Truck 3"
    truck3load[25] = float(distances[int(destination[24][8])][0])
    package_table.insert(25, (destination[24]))
    
    destination[27][9] = "Loaded on Truck 3"
    truck3load[28] = float(distances[int(destination[27][8])][0])
    package_table.insert(28, (destination[27]))
    
    destination[31][9] = "Loaded on Truck 3"
    truck3load[32] = float(distances[int(destination[31][8])][0])
    package_table.insert(28, (destination[31]))

    while len(truck3load) > 0: # truck 3 makes deliveries using the same formula as the other trucks
        for i in truck3load:
            deadline = destination[i-1][4]
            if deadline != "EOD":
                priority_list[i] = float(distances[int(destination[i-1][8])][int(truck3[0])])
        for i in priority_list: 
            truck3load.pop(i)
        while len(priority_list) > 0:
            next_stop(truck3, priority_list)
        
        if truck3[3] > datetime.timedelta(hours=10, minutes=20): # updates information for package 9 after 10:20
                if destination[8][6] == "Wrong address listed":
                    destination[8][1] = "410 S. State St."
                    destination[8][2] = "Salt Lake City"
                    destination[8][3] = "84111"
                    destination[8][6] = "Address has been updated"
                    destination[8][8] = 19 # updates index number for distances table

        next_stop(truck3, truck3load)

load_trucks() # begins load truck function
begin_deliveries() # begins delivery process

print("WGUPS Delivery and Package Information System\n")
print("All packages for today have been delivered.\n")
print("1. Show truck mileage at the end of the day")
print("2. Show status of all packages at a given time")
print("3. Show specific package information")
print("4. Exit\n")
option = input("Please select an option: ")

if option == "1":
    total_miles = truck1[2] + truck2[2] + truck3[2]
    print(f"\nTruck 1 mileage: {round(truck1[2], 1)}\nTruck 2 mileage: {round(truck2[2], 1)}\nTruck 3 mileage: {round(truck3[2], 1)}")
    print(f"\nAll packages delivered after {total_miles} miles\n")
    
if option == "2":
    timelist = {}    
    status_time = input("Enter a time in the format HH:MM ")
    (h, m) = status_time.split(":")
    status_time = datetime.timedelta(hours=int(h), minutes=int(m))
    for i in timestamps: # searches timestamp dictionary for all entries before the selected time
        if i < status_time:
            timelist[i] = timestamps[i] 
    snapshot = timelist[max(timelist.keys())] # selects the most recent snapshot from the reduced list
    for i in snapshot:
        print(f"Package ID #{i[0]} {i[9]}")

if option =="3":
    query = input("Please enter package ID #: ") # returns all information for the package id requested
    print(f"\nPackage ID #: {query}")
    print(f"Address: {package_table.search(int(query))[1]}") 
    print(f"City: {package_table.search(int(query))[2]}")
    print(f"Zip Code: {package_table.search(int(query))[3]}")
    print(f"Deadline: {package_table.search(int(query))[4]}")
    print(f"Weight: {package_table.search(int(query))[5]}")
    print(f"Status: Package {query} {package_table.search(int(query))[9]}")

if option == "4":
        quit() # exits program
