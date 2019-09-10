from lxml import html
import requests
import datetime

#global variables - settings
max_urls_per_array = 250 #sets the maximum urls that are allowed in an array, has to do with system memory

#global variables - counters
filecount_visited = 0
filecount_tovisit = 0

#global variables - arrays
newlinks = [] #for adding new links to the queue
links = [] #contains links currently being worked on
visited_links = [] #contains visited links
tempfile_store = [] #for storing file contents during transfer

logFile_queue = open(str(datetime.date.today()) + '_queue.log', '+w')
logFile_visits = open(str(datetime.date.today()) + '_visits.log', '+w')

def store_filecounts():
        with open('./datastore.txt', 'w') as datastore:
                data = []
                data.append(str(filecount_tovisit) + '\n')
                data.append(str(filecount_visited) + '\n')
                datastore.writelines(data)


def logQueue(string):
        logFile_queue.write(str(datetime.datetime.now()) + ' - ' + string + '\n')
        
def logVisit(string):
        logFile_visits.write(str(datetime.datetime.now()) + ' - ' + string + '\n')

def appendVisitedLink(URL):
        # add to array
        visited_links.append(URL)
        #is the array larger than the max?
        if len(visited_links) > max_urls_per_array:
                #yes, so move that amount to a file
                global filecount_visited
                with open('./visited/' + str(filecount_visited) + '.txt', 'w') as write_to_visited_file:
                        toWrite = visited_links[0:max_urls_per_array-1]
                        for item in range(len(toWrite)):
                                toWrite[item] = toWrite[item] + '\n'
                        write_to_visited_file.writelines(toWrite)
                #remove them from the array to save memory
                del visited_links[0:max_urls_per_array-1]
                filecount_visited = filecount_visited + 1
                store_filecounts()

def appendToVisitLink(URL):
        #add to array
        newlinks.append(URL)
        #is the array larger than the max?
        if len(newlinks) > max_urls_per_array:
                #yes, so move to file
                global filecount_tovisit
                with open('./tovisit/' + str(filecount_tovisit) + '.txt', 'w') as write_to_to_visit_file:
                        toWrite = newlinks[0:max_urls_per_array-1]
                        for item in range(len(toWrite)):
                                toWrite[item] = toWrite[item] + '\n'
                        write_to_to_visit_file.writelines(toWrite)
                #remove them from memory
                del newlinks[0:max_urls_per_array-1]
                filecount_tovisit = filecount_tovisit + 1
                store_filecounts()

def checkIfNotQueued(URL):
        try:
                #check if it is written in a file
                for i in range(filecount_tovisit):
                        with open('./tovisit' + str(i) + '.txt', 'r') as current_file_tovisit:
                                if URL + '\n' in current_file_tovisit.readlines():
                                        return False
        #the file is not found, pass
        except FileNotFoundError:
                pass
        #if another error occurs, notify and move on
        except:
                print('Unexpected error occurred reading to visit files, assuming not visited')
                pass
        #check if it is in memory
        if URL in newlinks:
                return False
        
        #check if it is in the currently being processed queue
        if URL in links:
                return False
        return True


def checkIfNotVisited(URL):
        try:
                #check if it is in one of the files
                for i in range(filecount_visited):
                        with open('./visited/' + str(i) + '.txt', 'r') as current_file_visited:
                                if URL + '\n' in current_file_visited.readlines():
                                        return False
        #if the file is not found, pass
        except FileNotFoundError:
                pass
        #if another error occurs, notify and assume it does not contain the link
        except:
                print('Unexpected error occurred reading visited files, assuming not visited')
                pass
        #check if it is in memory
        if URL in visited_links:
                return False
        #return true if it is not found
        return True

#Visit a specified webpage and query the results on if queued or if visited
def visitURL(URL):
        #get page and extract links
        current_page = requests.get(URL)
        current_tree_page = html.fromstring(current_page.content)
        current_page_urls = current_tree_page.xpath("//a/@href")
        #check for every new URL if it is already queued or visited
        for new_url in current_page_urls:
                if checkIfNotVisited(new_url):
                        #it is not visited, so is it already in the queue?
                        if checkIfNotQueued(new_url):
                                #It is not so queue it if it can probably be parsed
                                if new_url[0] == '/':
                                        print('Skipped ' + new_url + ', can not be parsed')
                                else:
                                        appendToVisitLink(new_url)
                                        print('Queued ' + new_url)
                                        logQueue('Queued ' + new_url)
                        else:
                                #it is already in the queue
                                print('Skipped ' + new_url + ', already queued')

                else:
                        #it was already visited
                        print('Skipped ' + new_url + ', already visited')
        appendVisitedLink(URL)
        print('Visited ' + URL)
        logVisit('Visited ' + URL)

if __name__ == "__main__":
        #load the firstrun flag from the file
        with open('./firstrun', 'r') as fr_file:
                firstrun_flag = fr_file.readlines()[0].rstrip('\n')
        #if it is a one, do the first run, else skip to the while loop
        if firstrun_flag == '1':
                first_url = input('Specify the starting URL: ')
                visitURL(first_url)
                #write all new links to a file, so the newlinks will be empty and links can be used for the first file
                with open('./tovisit/' + str(filecount_tovisit) + '.txt', 'w') as newlinks_file:
                        toWrite = []
                        for link in newlinks:
                                toWrite.append(link + '\n')
                        newlinks_file.writelines(toWrite)
                #increment to visit filecount by 1 to keep track of the new file
                filecount_tovisit = filecount_tovisit + 1
                store_filecounts()
                #set the first run flag to false
                with open('./firstrun', 'w') as fr_file:
                        fr_file.writelines(['0\n'])
        #if it is not the firstrun, get the filecounts
        else:
                with open('./datastore.txt', 'r') as datastore:
                        data = []
                        data_unformatted = datastore.readlines()
                        for item in data_unformatted:
                                data.append(item.rstrip('\n'))
                        filecount_tovisit = data[0]
                        filecount_visited = data[1]

        while True:
                #get the links from tovisit file 0
                links = []
                with open('./tovisit/0.txt', 'r') as readlinks:
                        unformatted_readlinks = readlinks.readlines()
                        for link in unformatted_readlinks:
                                links.append(link.rstrip('\n'))
                #visit the links from file 0
                for link in links:
                        try:
                                visitURL(link)
                        except:
                                print("could not load page " + link)
                #move all links one file down
                for filenum in range(filecount_tovisit):
                        try:
                                with open('./tovisit/' + str(filenum + 1) + '.txt', 'r') as readfile:
                                        with open('./tovisit/' + str(filenum) + '.txt', 'w') as writefile:
                                                writefile.writelines(readfile.readlines())
                        except:
                                print('Error loading file index ' + str(filenum) + " and " + str(filenum+1))
                                pass
                filecount_tovisit = filecount_tovisit - 1
                store_filecounts()
