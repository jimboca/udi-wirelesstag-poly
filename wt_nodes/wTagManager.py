"""
This is a NodeServer for CAO Gadgets Wireless Sensor Tags for Polyglot v2 written in Python3
by JimBoCA jimboca3@gmail.com
"""
import polyinterface
import sys
import time
from wt_funcs import get_valid_node_name
from wt_nodes import wTag

LOGGER = polyinterface.LOGGER

class wTagManager(polyinterface.Node):
    """
    This is the class that all the Nodes will be represented by. You will add this to
    Polyglot/ISY with the controller.addNode method.

    Class Variables:
    self.primary: String address of the Controller node.
    self.parent: Easy access to the Controller Class from the node itself.
    self.address: String address of this Node 14 character limit. (ISY limitation)
    self.added: Boolean Confirmed added to ISY

    Class Methods:
    start(): This method is called once polyglot confirms the node is added to ISY.
    setDriver('ST', 1, report = True, force = False):
        This sets the driver 'ST' to 1. If report is False we do not report it to
        Polyglot/ISY. If force is True, we send a report even if the value hasn't changed.
    reportDrivers(): Forces a full update of all drivers to Polyglot/ISY.
    query(): Called when ISY sends a query request to Polyglot for this specific node
    """
    def __init__(self, controller, address, name, mac=None, new=False):
        """
        Optional.
        Super runs all the parent class necessities. You do NOT have
        to override the __init__ method, but if you do, you MUST call super.

        :param controller: Reference to the Controller class
        :param primary: Controller address
        :param address: This nodes address
        :param name: This nodes name
        """
        # Save the real mac before we legalize it.
        self.mac      = mac
        self.new      = new
        address = get_valid_node_name(mac)
        super(wTagManager, self).__init__(controller, address, address, name)

    def start(self):
        """
        Optional.
        This method is run once the Node is successfully added to the ISY
        and we get a return result from Polyglot. Only happens once.
        """
        self.set_st(True)
        if self.new:
            self.set_use_tags(0)
        else:
            self.set_use_tags(self.getDriver('GV1'))
            self.l_info("start",'{0} {1}'.format(self._drivers,self.use_tags))
        self.degFC = 1 # I like F.
        self.discover()
        self.query()


    def query(self):
        """
        Called by ISY to report all drivers for this node. This is done in
        the parent class, so you don't need to override this method unless
        there is a need.
        """
        self.reportDrivers()

    def discover(self):
        self.l_debug('discover','use_tags={}'.format(self.use_tags))
        if self.use_tags == 0:
            return False
        ret = self.get_tag_list()
        if ret['st'] is False:
            return
        index = 0
        for tag in ret['result']:
            self.l_debug('discover','Got Tag: {}'.format(tag))
            tag['tid'] = index
            self.controller.addNode(wTag(self.controller, self.address, tdata=tag))
    """
    Misc functions
    """

    def get_tag_list(self):
        ret = self.controller.wtServer.SelectTagManager(self.mac)
        if ret['st'] is False:
            self.set_st(False)
            self.l_error('get_tag_list',"Unable to select tag manager: {}".format(self.mac))
        else:
            ret = self.controller.wtServer.GetTagList()
            if ret['st'] is False:
                self.set_st(False)
                self.l_error('get_tag_list',"Unable to select get tags")
            else:
                self.set_st(True)
        return ret
    
    def l_info(self, name, string):
        LOGGER.info("%s:%s:%s: %s" %  (self.id,self.name,name,string))
        
    def l_error(self, name, string):
        LOGGER.error("%s:%s:%s: %s" % (self.id,self.name,name,string))
        
    def l_warning(self, name, string):
        LOGGER.warning("%s:%s:%s: %s" % (self.id,self.name,name,string))
        
    def l_debug(self, name, string):
        LOGGER.debug("%s:%s:%s: %s" % (self.id,self.name,name,string))

    """
    Set Functions
    """
    def set_params(self,params):
        """
        Set params from the getTagManager data
        """
        self.set_st(params['online'])

    def set_st(self,value,force=False):
        if not force and hasattr(self,"st") and self.st == value:
            return True
        self.st = value
        if value:
            self.setDriver('ST', 1)
        else:
            self.setDriver('ST', 0)

    def set_use_tags(self,value,force=False):
        value = int(value)
        if not force and hasattr(self,"use_tags") and self.use_tags == value:
            return True
        self.use_tags = value
        self.setDriver('GV1', value)

    """
    """

    def cmd_set_use_tags(self,command):
        self.set_use_tags(command.get("value"))

    def cmd_set_on(self, command):
        """
        Example command received from ISY.
        Set DON on MyNode.
        Sets the ST (status) driver to 1 or 'True'
        """
        self.setDriver('ST', 1)

    def cmd_set_off(self, command):
        """
        Example command received from ISY.
        Set DOF on MyNode
        Sets the ST (status) driver to 0 or 'False'
        """
        self.setDriver('ST', 0)

    
    id = 'wTagManager'
    drivers = [
        {'driver': 'ST',  'value': 0, 'uom': 2},
        {'driver': 'GV1', 'value': 1, 'uom': 2}  # Use Tags
    ]
    commands = {
        'SET_USE_TAGS': cmd_set_use_tags,
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
    }