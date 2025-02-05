# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fakeIP
   Description :
   Author :       CoolCat
   date：          2019-06-05
-------------------------------------------------
   Change Activity:
                   2019-06-05:
-------------------------------------------------
"""
__author__ = 'CoolCat'
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import random
from burp import ITab
from javax.swing import JMenu
from javax.swing import JMenuItem
from burp import IBurpExtender
from burp import IHttpListener
from java.io import PrintWriter
from burp import IContextMenuFactory
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from java.awt import GridBagLayout, GridBagConstraints
from javax.swing import JLabel, JTextField, JOptionPane, JTabbedPane, JPanel, JButton
from struct import pack
from socket import inet_ntoa
from random import randint


add_headers = [
    'X-Forwarded-For: ', 'X-Forwarded: ', 'Forwarded-For: ', 'Forwarded: ', 'X-Forwarded-Host: ', 
    'X-remote-IP: ', 'X-remote-addr: ', 'True-Client-IP: ', 'X-Client-IP: ', 'Client-IP: ', 
    'X-Real-IP: ', 'Ali-CDN-Real-IP: ', 'Cdn-Src-Ip: ', 'Cdn-Real-Ip: ', 'CF-Connecting-IP: ', 
    'X-Cluster-Client-IP: ', 'WL-Proxy-Client-IP: ', 'Proxy-Client-IP: ', 'Fastly-Client-Ip: ',
    'True-Client-Ip: ', 'X-Originating-IP: ', 'X-Host: ', 'X-Custom-IP-Authorization: '
    ]

class BurpExtender(IBurpExtender, IHttpListener, IContextMenuFactory, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):

        print "[+] #####################################"
        print "[+]    fakeIp for burp V1.0"
        print "[+]    anthor: CoolCat"
        print "[+]    email: CoolCat@gzsec.org"
        print "[+]    gayhub:https://github.com/TheKingOfDuck"
        print "[+] #####################################"

        print "\n[-]fakeIp loading..."

        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("fakeIp")
        callbacks.registerHttpListener(self)
        callbacks.registerContextMenuFactory(self)
        self.stdout = PrintWriter(callbacks.getStdout(), True)
        self.stderr = PrintWriter(callbacks.getStderr(), True)
        callbacks.issueAlert("Loaded Successfull.")

        # obtain an extension helpers object
        self._helpers = callbacks.getHelpers()

        # register ourselves as an Intruder payload generator
        callbacks.registerIntruderPayloadGeneratorFactory(self)

        print "[*]Successfull..."

    def createMenuItems(self, invocation):
        self.menus = []
        self.mainMenu = JMenu("fakeIp")
        self.menus.append(self.mainMenu)
        self.invocation = invocation
        # print invocation.getSelectedMessages()[0].getRequest()
        menuItem = ['inputIP', '127.0.0.1', 'randomIP', '0x2130706433']
        for tool in menuItem:
            # self.mainMenu.add(JMenuItem(tool))
            if tool == 'inputIP':
                menu = JMenuItem(tool, None, actionPerformed=lambda x: self.modifyHeader(x))
                self.mainMenu.add(menu)
            elif tool == '127.0.0.1':
                menu = JMenuItem(tool, None, actionPerformed=lambda x: self.modifyHeader(x))
                self.mainMenu.add(menu)
            elif tool == 'randomIP':
                menu = JMenuItem(tool, None, actionPerformed=lambda x: self.modifyHeader(x))
                self.mainMenu.add(menu)
            elif tool == '0x2130706433':
                menu = JMenuItem(tool, None, actionPerformed=lambda x: self.modifyHeader(x))
                self.mainMenu.add(menu)

        return self.menus if self.menus else None

    def addIPs(self, ip):

            currentRequest = self.invocation.getSelectedMessages()[0]  # getSelectedMessages()返回数组，但有时为1个，有时2个
            requestInfo = self._helpers.analyzeRequest(currentRequest)  # 该部分实际获取到的是全部的Http请求包
            self.headers = list(requestInfo.getHeaders())

            if isinstance(ip,list):
                for i in range(0,len(add_headers)):
                    self.headers.append(add_headers[i] + ip[i])
            else:
                for hs in add_headers:
                    self.headers.append(hs + ip)

            # print 'self.headers',self.headers
            bodyBytes = currentRequest.getRequest()[requestInfo.getBodyOffset():]  # bytes[]类型
            self.body = self._helpers.bytesToString(bodyBytes)  # bytes to string转换一下
            # print 'self.body:',self.body
            newMessage = self._helpers.buildHttpMessage(self.headers, self.body)
            currentRequest.setRequest(newMessage)  # setRequest() 会动态更新setRequest\


    def modifyHeader(self, x):
        if x.getSource().text == 'inputIP':  # 通过获取当前点击的子菜单的 text 属性，确定当前需要执行的 command
            ip = JOptionPane.showInputDialog("Pls input ur ip:");

            self.addIPs(ip)
        elif x.getSource().text == '127.0.0.1':
            self.addIPs("127.0.0.1")
        
        elif x.getSource().text == '0x2130706433':
            self.addIPs("2130706433")

        elif x.getSource().text == 'randomIP':
            IPS = []
            for hs in add_headers:
                IPS.append(inet_ntoa(pack('I',randint(1,0xffffffff))))
            self.addIPs(IPS)

    def getGeneratorName(self):
        return "fakeIpPayloads"

    def createNewInstance(self, attack):
        return fakeIpGenerator(self, attack)


# 定义fakeIpGenerator类，扩展了IIntruderPayloadGenerator类
# 增加了max_payload(最大的payload), num_iterations(迭代次数)两个变量，用于控制模糊测试的次数
class fakeIpGenerator(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        self.max_payload = 1
        self.num_iterations = 0
        return

    # 通过比较判断迭代是否达到上限
    def hasMorePayloads(self):
        if self.num_iterations == self.max_payload:
            return False
        else:
            return True

    # 接受原始的HTTP负载，current_payload是数组，
    def getNextPayload(self, current_payload):
        return inet_ntoa(pack('I',randint(1,0xffffffff)))
