
LOG_FILENAME = 'logs/run.log'
ERR_FILENAME = 'logs/run.err'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Debug:
    def __init__(self, log_filename = LOG_FILENAME):
        self.kill_on_assrt = True
        self.curr_log_level = 0 # 0 - tmp prints. 
                                # 1 - logs. 
                                # 2 - errors
        self.flog = open(LOG_FILENAME, 'w')
        self.ferr = open(ERR_FILENAME, 'w')

    def logger(self, msg, log_level = 0):
        if log_level >= self.curr_log_level:
            msg=msg+"\n"
            if log_level == 2:
                print (bcolors.WARNING + msg + bcolors.ENDC)
            else:
                print(msg)
            self.flog.write(msg)
            if log_level == 2:
                self.ferr.write(msg)

    def close():
        self.flog.close()
        self.ferr.close()

    def assrt(self, cond, msg):
        if not cond:
            self.logger (msg, 2)
            if self.kill_on_assrt:
               exit(1)
