# -*- coding: utf-8 -*-
import logging
import numpy as np


class Instance():
    def __init__(self, sim_setting):

        logging.info("starting simulation...")
        self.total_node = sim_setting['total_node']
        
        self.costs = np.random.randint(
            sim_setting['min_cost'],
            sim_setting['max_cost'],
            sim_setting['total_node']
        )
        # self.profits = np.around(np.random.uniform(
        #     sim_setting['low_profit'],
        #     sim_setting['high_profit'],
        #     sim_setting['n_items']
        # ))
        # self.n_items = sim_setting['n_items']
        # logging.info("simulation end")

    def get_data(self):
        """[summary]
        
        Returns:
            [type] -- [description]
        """
        logging.info("getting data from instance...")
        return {
            "costs": self.costs,
            # "sizes": self.sizes,
            # "max_size": self.max_size,
            # "n_items": self.n_items
        }
