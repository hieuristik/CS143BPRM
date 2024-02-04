FREE_DICT = {0: False,
             1: False,
             2: False,
             3: False,
             4: False,
             5: False,
             6: False,
             7: False,
             8: False,
             9: False,
             10: False,
             11: False,
             12: False,
             13: False,
             14: False,
             15: False}


RL = { 2: list(),
       1: list(),
       0: list()}


BL = list()


DELETE_LIST = list()


def free_all_processes():
    for key in FREE_DICT:
        FREE_DICT[key] = False


def free_ready_list():
    for key in RL:
        RL[key].clear()


def check_pcb_overflow():
    for index, allo in FREE_DICT.items():
        if not allo:
            return index
    return -1


def addByPriority(process, p):
    for priority, lst in RL.items():
        if priority == p:
            lst.append( process )


def scheduler():
    for key in RL:
        if not RL[key]: continue
        return


def timeout():
    for ll in RL.values():
        if not ll: continue # check if linked list is empty
        temp = ll.pop(0)
        ll.append( temp )
        break
    scheduler()
    return


def getRunning():
    for key in RL:
        if not RL[key]: continue
        return RL[key][0].index


def getAllChildren(process):
    if (process.children):
        for children in process.children:
            getAllChildren( children )
    DELETE_LIST.append( process.index )


def findProcessByIndex(i):
    for ll in RL.values():
        for process in ll:
            if process.index == i: return process
    return None


def checkBlocked(i):
    for p in BL:
        if (p.index == i and p.state == 0): return True
    return False


def removeFromRLByIndex(i):
    for ll in RL.values():
        for (idx, p) in enumerate(ll):
            if p.index == i:
                ll.pop( idx )
                return


def handle_input(line, m):
    if line.startswith("cr"):
        priority = int(line.split()[1])                               # parse user input for priority
        if (priority == 0 or priority > 2) or check_pcb_overflow() == -1:
            return -1
        pcb = m._PCB[ m._running ].create( priority )                   # simulate running process creating new process at specified priority
        if ( type(pcb) is int and pcb == -1):
            return -1
        m._running = getRunning()                                       # update the current running process
        m._PCB[ pcb.index ] = pcb                                       # update manager's _PCB list
        return m._running                               # print out index of process running next
    elif line.startswith("de"):
        delete_index = int(line.split()[1])                           # parse user input for target index to delete process
        if (delete_index <= 0 or delete_index > 15):                    # error thrown if index is invalid
            return -1
        if not FREE_DICT[delete_index]: return -1                       # can't delete pcb that doesn't exist yet
        getAllChildren( m._PCB[ delete_index ] )                        # get all children of target index in order to clear _PCB list
        m._PCB[ m._running ].destroy( delete_index )                    # current running process will call destroy function
        for idx in DELETE_LIST:                                         # freeing processes in _PCB list
            FREE_DICT[idx] = False
            m._PCB[idx] = None
        DELETE_LIST.clear()
        m._running = getRunning()                                       # update the current running process
        return m._running                                 # print out index of process running next                                         
    elif line.startswith("rq"):                                       
        args = line.split()                                           
        ridx, units = int(args[1]), int(args[2])                                  
        if (ridx >= 0 and ridx <= 3):                                   
            if ( ((ridx == 0 or ridx == 1) and units > 1) or ((ridx == 2) and units > 2) or ((ridx == 3) and units > 3) ):
                return -1                                                                                             
        else:                                                           
            return -1                                                                                                 
        response = m._PCB[ m._running ].request( m._RCB[ridx], units )  # running process requesting resource at index: ridx with units: units
        if (response == -1):
            return -1
        m._running = getRunning()           # RL will handle whether or not the process has been blocked
        return m._running     # if process is blocked, process will be removed from RL and current running process will be updated
    elif line.startswith("rl"):
        args = line.split()
        ridx, units = int(args[1]), int(args[2])
        if (ridx >= 0 and ridx <= 3):
            if ( ((ridx == 0 or ridx == 1) and units > 1) or ((ridx == 2) and units > 2) or ((ridx == 3) and units > 3) ):
                return -1
        else:
            return -1
        r = (m._RCB[ridx], units)
        response = m._PCB[ m._running ].release( r )
        if (response == -1):
            return -1
        m._running = getRunning()
        return m._running
    elif line.__eq__("to") or line.__eq__("to\n"):
        timeout()
        m._running = getRunning()
        return m._running
    elif line.__eq__("in") or line.__eq__("in\n"):
        m.init()
        return m._running
    else: return -2


class RCB:
    def __init__(self, state, index):
        self.state = state       # 0 indicates all units have been allocated
        self.waitlist = list()   # linked list of processes blocked on this resource
        self.index = index

class PCB:
    def __init__(self, priority=0):
        self.state = 1              # 1 indicates ready, 0 indicates blocked
        self.parent = None          # parent designated later
        self.children = list()      # linked list of processes that this process has created
        self.resources = list()     # linked list of resources that this process is currently holding
        self.priority = priority
        self.index = 0
    
    """
    HELPER FUNCTIONS [START]
    """
    def checkHoldingResource(self, index):
        for resource in self.resources:
            if (resource[0].index == index): return True
        return False
    
    def  checkOverReleasing(self, index, amtReleasing):
        count = 0
        for resource in self.resources:
            if (resource[0].index == index):
                count += resource[1]
        if (count < amtReleasing): return False
        return True
    
    """
    HELPER FUNCTIONS [END]
    """

    def create(self, p):
        index = check_pcb_overflow()
        if (index == -1): return -1                    
        newPCB = PCB(p)                  
        newPCB.index = index             
        FREE_DICT[index] = True          # indicate that new process at specified index has been allocated
        self.children.append( newPCB )
        newPCB.parent = self
        addByPriority(newPCB, p)
        scheduler()
        return newPCB
    
    def destroy(self, j): # j is the target index of some process, but this can be handled during shell call
        blocked_process = None
        if ( checkBlocked( j ) ):
            for (i, b) in enumerate( BL ):
                if b.index == j:
                    blocked_process = b
                    BL.pop( i )
                    break
        process = blocked_process if blocked_process else findProcessByIndex( j )
        temp_children_list = process.children.copy()
        for child in temp_children_list:
            process.destroy( child.index )
        for child_index, p in enumerate( process.parent.children ):
            if process.index == p.index:
                process.parent.children.pop( child_index )
        if process.state == 1:
            removeFromRLByIndex( process.index )
        for res in process.resources:
            process.release( res )
        scheduler()

    
    def request(self, r, k): # r is _RCB object, k is amount of units
        if (self.index == 0):
            return -1
        temp = None
        if r.state >= k:
            r.state = r.state - k 
            self.resources.append( (r, k) )
        else:
            self.state = 0 # indicates blocked
            for ll in RL.values():
                if not ll: continue
                temp = ll.pop(0)
                break
            r.waitlist.append( (temp, k) )
            BL.append( temp )
            scheduler()

    def release(self, r): # r is a tuple (resource_object, units)
        if (self.checkHoldingResource(r[0].index) == False):
            return -1
        if (self.checkOverReleasing(r[0].index, r[1]) == False):
            return -1
        k = 0
        temp = r[1]
        for (idx, resource) in enumerate(self.resources):               # resource is a tuple
            if r[0].index == resource[0].index and temp > 0:            # check to make sure of correct RCB and that units still need to be released
                if (resource[1] <= r[1]): k += resource[1]              # check to make sure that units match up
                temp -= resource[1]                                     # modify temp, if temp > 0 continue looping for resources, if not exit the loop
                self.resources[idx] = None                              # flag the index for later removal of resource
        while (None in self.resources):
            self.resources.remove(None)
        r[0].state += k
        while (r[0].waitlist and r[0].state > 0):
            process, units = r[0].waitlist[0]
            if (r[0].state >= units):
                r[0].state = r[0].state - units
                process.resources.append( (r[0], units) )
                process.state = 1
                r[0].waitlist.pop(0)
                for (priority, lst) in RL.items():
                    if process.priority == priority:
                        lst.append( process )
            else: break
        scheduler()

            
class Manager:
    def __init__(self):
        self._PCB = None
        self._RCB = None
        self._running = None

    def init(self):
        free_all_processes()    # Reset FREE_DICT

        self._PCB = [None for _ in range(16)]
        self._PCB[0] = PCB() # setting up PCB[0]
        FREE_DICT[0] = True
        
        self._RCB = [None for _ in range(4)]
        for idx in range(len(self._RCB)):
            if idx <= 1:
                self._RCB[idx] = RCB(1, idx)
            if (idx == 2): 
                self._RCB[idx] = RCB(2, idx)
            if (idx == 3): 
                self._RCB[idx] = RCB(3, idx)
        
        free_ready_list()
        DELETE_LIST.clear()
        BL.clear()

        addByPriority( self._PCB[0], 0 )
        self._running = 0


if __name__ == "__main__":
    man = Manager()
    output = ""

    opt = input()

    if len(opt) > 0:
        input_file_path = opt

        write_lines = list()
        read_lines = None

        with open(input_file_path, 'r') as infile:
            read_lines = infile.readlines()

        for l in read_lines:
            res = handle_input(l, man)
            if (res == -2):
                write_lines.append( '\n' )
                continue
            elif (res == -1):
                write_lines.append( str(-1) )
            else:
                write_lines.append( str(res) + " " )

        with open('output.txt', 'w+') as outfile:
            outfile.writelines( write_lines )
        
    elif opt == "":
        print( "-"*5 + "MANUAL TESTING" + "-"*5 )
        opt = None
        while(True):
            for key in RL:
                print(f"level {key}: {[p.index for p in RL[key]]}")
            opt = input()
            res = handle_input(opt, man)
            if (res == -2): break
            elif (res == -1):
                output += str(-1) + '\n'
                print()
            else:
                output += str(res) + " "
            opt = None
        print( output )
    else:
        print("error")