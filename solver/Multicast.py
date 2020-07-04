# -*- coding: utf-8 -*-
import time
import logging
import json
from pulp import *
import networkx as nx

class MultiCast():
    def __init__(self):
        pass
    def group_exctractor(self,group):
        normal_nodes = self.all_nodes.copy()
        gp_source = group['source']# extract source node for group n
        gp_destinations = []# extract source destination nodes for group n
        sd_nodes = []# extract source or destinations node for group n
        sd_nodes.append(group['source'])
        for d in range(len(group['destinations'])):
            sd_nodes.append(group['destinations'][d])
            gp_destinations.append(group['destinations'][d])
        for node in sd_nodes: #extract nodes which are neither source nor destination for group n
            normal_nodes.remove(node)
        g_num = int(group['group_number']) #extract group number
        return normal_nodes,g_num,gp_source,gp_destinations
    def solve(
        self, G, 
        # simple_data,
        matrix,
        gp_container,
        # time_limit=None,
        # gap=None, verbose=False
        ):  
        fp = open("./etc/config.json", 'r')
        sim_setting = json.load(fp)
        fp.close()

        self.all_nodes = [i for i in G.nodes]            
        n_nodes = range(G.order())
        
        #defining Variables
        xe = LpVariable.dicts(
            "X", [(i,j,g)for g in range(1,sim_setting['n_multicast_group']+1) for i in n_nodes for j in n_nodes],
            lowBound=0,
            upBound=1,
            cat=LpBinary
            )
        f = LpVariable.dicts(
            "F",[(i,j,g)for g in range(1,sim_setting['n_multicast_group']+1) for i in n_nodes for j in n_nodes],
            lowBound=0,
            # upBound=sim_setting['num_destination'],
            cat=LpInteger
            )
        
        # return V,E,D,xe,f_ij
        # return xe

        problem_name = "MultiCast"
        
        prob = LpProblem(problem_name, LpMinimize)
        #defining OJ
        # prob += lpSum([matrix[i][j] * xe[(i,j,g)] for g in range(3) for i in n_nodes for j in n_nodes]) , "obj_func"
        prob += lpSum(lpSum([matrix[i][j] * xe[(i,j,g)] for i in n_nodes for j in n_nodes]) for g in range(1,len(gp_container)+1)), "obj_func"

    
        #defining constraint       
        ############ constraint 1 on Formula ############
        for group in gp_container:
            temp = self.group_exctractor(group)
            normal_nodes= temp[0]
            g = temp[1]
            for i in normal_nodes:
                prob += lpSum([f[(i,j,g)] for j in n_nodes if matrix[i][j]])-lpSum([f[(k,i,g)]for k in n_nodes if matrix[k][i]]) == 0, '1-in group {} flow balance for node {}'.format(g,i)
                # f'flow balance for node{i} in group {g}'
       
        ############ constraint 2 on Formula ############ 
        for group in gp_container:
            temp = self.group_exctractor(group)
            normal_nodes= temp[0]
            g = temp[1]
            source = temp[2]
            prob += lpSum([f[(source,j,g)] for j in n_nodes if matrix[source][j]]) == int(sim_setting['num_destination']), "2-output flow from group {}'s source" .format(g)
        
        ############ constraint 3 on Formula ############ 
        for group in gp_container:
            temp = self.group_exctractor(group)
            normal_nodes= temp[0]
            g = temp[1]
            destinations = temp[3]
            for d in destinations:
                prob += lpSum([f[(i,d,g)] for i in n_nodes if matrix[i][d]]) == 1 ,'3-in group {} input flow to destination {}'.format(g,d)
        
        
        ############ constraint 4 on Formula ############
        # ex_dest = normal_nodes+source
        for group in gp_container:
            temp = self.group_exctractor(group)
            g = temp[1]
            for i in self.all_nodes:
                for j in self.all_nodes:
                # for j in ex_dest:
                      if matrix[i][j]:
                        prob += f[(i,j,g)] <= (int(sim_setting['num_destination'])*xe[(i,j,g)]) ,'4-in group {} Max flow allowed on edge ({},{})'.format(g,i,j)
        
        ############ constraint 5 on Formula ############
        for i in self.all_nodes:
            for j in self.all_nodes: 
                if matrix[i][j]:
                    prob += lpSum(xe[(i,j,g)] for g in range(1,len(gp_container)+1)) <= int(sim_setting['h']), '5-Max #({},{}) allowed to be chosen'.format(i,j)
                    
        ############ constraint new on Formula ############
        for group in gp_container:
            temp = self.group_exctractor(group)
            g = temp[1]
            source = temp[2]
            prob += lpSum([f[(i,source,g)] for i in n_nodes if matrix[i][source]]) == 0, '6-in group {} no input to source'.format(g)
        #writes LP model, provided by pulp
        
        prob.writeLP("./logs/{}.lp".format(problem_name))

        # # msg_val = 1 if verbose else 0
        # start = time.time()
        # prob.solve(solver=COIN_CMD())
        # end = time.time()
        # logging.info("\t Status: {}".format(pulp.LpStatus[prob.status]))
        # # print(pulp.LpStatus[prob.status])

        # sol = prob.variables()
        # of = value(prob.objective)
        # comp_time = end - start
        
        # sol_x = []
        # sol_f = []
        # for var in sol:
        #     logging.info("{} {}".format(var.name, var.varValue))
        #     x_name = var.name
        #     x_value =  var.varValue
        #     if "X_" in var.name:
        #         if x_value != 0:
        #             sol_x.append(var.name.replace("X_", ""))
        #     if "F_" in var.name:
        #         if x_value !=0:
        #             sol_f.append((var.name.replace("F_", ""),var.varValue))
        # logging.info("\n\tof: {}\n\tsol:\n{} \n\ttime:{}".format(of, sol_x, comp_time))
        # logging.info("#########")
        
        # return of,sol_x,sol_f,comp_time,destinations,source,normal_nodes
