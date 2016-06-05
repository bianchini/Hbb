

FitCfg = {

    # POLYDIJET    
    "polydijet": {

        # degree
        "deg1": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [5.0, 20.0],
                    "a1" : [-0.02, +0.30],
                    },
                "test1": {
                    "a0" : [+10.0, +12.0],
                    "a1" : [-0.05, +0.20],
                    },
                },        
            },

        # degree
        "deg2": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [6.0, 10.0],
                    "a1" : [+0.02, +0.08],
                    "a2" : [+35., +100.],
                    },
                "test1": {
                    "a0" : [+10.0, +12.0],
                    "a1" : [-0.05, +0.20],
                    "a2" : [+35., +100.],
                    },
                },        
            },

        # degree
        "deg3": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [6.0, 10.0],
                    "a1" : [+0.02, +0.08],
                    "a2" : [+35., +100.],
                    "a3" : [-1.0e+04, +1.0e+04],
                    },
                "test1": {
                    "a0" : [+10.0, +12.0],
                    "a1" : [-0.05, +0.20],
                    "a2" : [+35., +100.],
                    "a3" : [-1.0e+04, +1.0e+04],
                    },
                },        
            },

        
        }, # END POLYDIJET

   
    }
