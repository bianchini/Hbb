
FitSgnCfg = {
    "Spin0_M650" : {
        'mean' : [550.,650.],
        'sigma' : [30., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1300.],
        'bias' : 0.01,
        },
    "Spin0_M750" : {
        'mean' : [650.,750.],
        'sigma' : [20., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1300.],
        'bias' : 0.01,
        },
    "Spin0_M850" : {
        'mean' : [750.,900.],
        'sigma' : [20., 200.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1300.],
        'bias' : 0.01,
        },
    "Spin0_M1000" : {
        'mean' : [800.,1100.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1400.],
        'bias' : 0.01,
        },
    "Spin0_M1200" : {
        'mean' : [900.,1300.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1500.],
        'bias' : 0.01,
        },
    "Spin2_M650" : {
        'mean' : [550.,650.],
        'sigma' : [30., 100.],
        'xi' : [-3., +3.],
        'rho1' : [-1.0, +1.0],
        'rho2' : [-1.0, +1.0],
        'fit_range' : [400., 900.],
        'bias' : 0.01,
        },
    "Spin2_M750" : {
        'mean' : [650.,750.],
        'sigma' : [20., 100.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1000.],
        'bias' : 0.01,
        },
    "Spin2_M850" : {
        'mean' : [750.,900.],
        'sigma' : [20., 200.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1100.],
        'bias' : 0.01,
        },
    "Spin2_M1000" : {
        'mean' : [800.,1100.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [400., 1200.],
        'bias' : 0.01,
        },
    "Spin2_M1200" : {
        'mean' : [900.,1300.],
        'sigma' : [50., 400.],
        'xi' : [-3., 3.],
        'rho1' : [-1., 1.],
        'rho2' : [-1., 1.],
        'fit_range' : [600., 1400.],
        'bias' : 0.01,
        }
    }


FTestCfg = {
    "pol" : {
        "FirstOrder" : 6,
        "LastOrder" : 8,
        "Match" : -1,
        "MaxOrder" : 7, #6,
        "ndof" : 6,
        "fit_range" : [400., 1200.], 
        },
    "exp" : {
        "FirstOrder" : 1,
        "LastOrder" : 3,
        "Match" : -1,
        "MaxOrder" : 3, #3,
        "ndof" : 3, #3,
        "fit_range" : [400., 1200.], 
        },
    "pow" : {
        "FirstOrder" : 1,
        "LastOrder" : 4,
        "Match" : -1,
        "MaxOrder" : 3,
        "ndof" : 3,
        "fit_range" : [400., 1200.], 
        },
    "polyexp" : {
        "FirstOrder" : 1,
        "LastOrder" : 4,
        "Match" : -1,
        "MaxOrder" : 3,
        "ndof" : 3,
        "fit_range" : [400., 1200.], 
        },
    "dijet" : {
        "FirstOrder" : 1,
        "LastOrder" : 5,
        "Match" : -1,
        "MaxOrder" : 2,
        "ndof" : 2,
        "fit_range" : [400., 1200.], 
        },
    "polydijet" : {
        "FirstOrder" : 2,
        "LastOrder" : 2,
        "Match" : -1,
        "MaxOrder" : 2,#2
        "ndof" : 3,#3
        "fit_range" : [400., 1200.], 
        },
    "expdijet" : {
        "FirstOrder" : 1,
        "LastOrder" : 3,
        "Match" : -1,
        "MaxOrder" : 3,
        "ndof" : 3,
        "fit_range" : [400., 1200.], 
        },
    }


FitBkgCfg = {

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
                    "a0" : [+8.50, +12.50],
                    "a1" : [+0.06, +0.10],
                    },
                },
            "400to800" : {                
                # parameter sets
                "default": {
                    "a0" : [5.0, 20.0],
                    "a1" : [-0.1, +0.3],
                    },
                },        
            "450to800" : {                
                # parameter sets
                "default": {
                    "a0" : [5.0, 20.0],
                    "a1" : [-0.1, +0.3],
                    },
                },        
            "800to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [2.0, 8.0],
                    "a1" : [-0.1, +0.1],
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
                # old one
                "test1": {
                    "a0" : [+10.0, +12.0],
                    "a1" : [-0.05, +0.20],
                    "a2" : [+35., +100.],
                    },
                },        
            "400to800" : {                
                # parameter sets
                "default": {
                    "a0" : [6.0, 10.0],
                    "a1" : [+0.02, +0.08],
                    "a2" : [+35., +100.],
                    }
                },        
            "450to800" : {                
                # parameter sets
                "default": {
                    "a0" : [6.0, 10.0],
                    "a1" : [+0.02, +0.08],
                    "a2" : [+35., +100.],
                    }
                },        
            "500to900" : {                
                # parameter sets
                "default": {
                    "a0" : [6.0, 10.0],
                    "a1" : [+0.02, +0.08],
                    "a2" : [+35., +100.],
                    }
                },        
            "600to1000" : {                
                # parameter sets
                "default": {
                    "a0" : [8.0, 14.0],
                    "a1" : [+0.03, +0.10],
                    "a2" : [+35., +250.],
                    },
                 "test1": {
                    "a0" : [8.0, 14.0],
                    "a1" : [+0.03, +0.10],
                    "a2" : [+35., +150.],
                    }
                },        
            "700to1200" : {                
                # parameter sets
                "default": {
                    "a0" : [2.0, 10.0],
                    "a1" : [-0.01, +0.10],
                    "a2" : [+20., +140.],
                    },
                "test1": {
                    "a0" : [2.0, 10.0],
                    "a1" : [-0.01, +0.10],
                    "a2" : [+20., +140.],
                    }
                },        
            "700to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [2.0, 10.0],
                    "a1" : [-0.01, +0.10],
                    "a2" : [+20., +140.],
                    },
                #"default": {
                #    "a0" : [1.0, 10.0],
                #    "a1" : [-0.50, +0.10],
                #    "a2" : [+20., +250.],
                #    },
                "test1": {
                    "a0" : [2.0, 10.0],
                    "a1" : [-0.10, +0.10],
                    "a2" : [+17., +250.],
                    }
                },
            "800to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [1.0, 10.0],
                    "a1" : [-0.50, +0.10],
                    "a2" : [+17., +250.],
                    },
                "test1": {
                    "a0" : [2.0, 10.0],
                    "a1" : [-0.10, +0.10],
                    "a2" : [+17., +250.],
                    }
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
                },
            },
        
        }, # END POLYDIJET


    # DIJET    
    "dijet": {

        # degree
        "any": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [0.0, 15.0],
                    "a1" : [-0.05, +0.2],
                    "a2" : [0.0, 1.0e-04],
                    "a3" : [200.,450.],
                    "a4" : [100., 300.],
                    },
                },        
            },
        }, # END DIJET


    # POL
    "pol": {
        # degree
        "any": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [-1.0, +1.0],
                    "a1" : [-1.0, +1.0],
                    "a2" : [-1.0, +1.0],
                    "a3" : [-1.0, +1.0],
                    "a4" : [-1.0, +1.0],
                    "a5" : [-1.0, +1.0],
                    "a6" : [-1.0, +1.0],
                    "a7" : [-1.0, +1.0],
                    "a8" : [-1.0, +1.0],
                    },
                },        
            },
        }, # END POL

    # EXP
    "exp": {
        # degree
        "any": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015, -0.013],
                    "a1" : [+0.5e-06, +2e-05],
                    "a2" : [-1.0e-9, -1.0e-10],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                },                    
            "400to800" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.020, -0.005],
                    "a1" : [+1.0e-06, +1e-05],
                    "a2" : [+1.0e-12, +1.0e-9],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                },                    
            "450to800" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.020, -0.005],
                    "a1" : [+1.0e-06, +1e-05],
                    "a2" : [+1.0e-12, +1.0e-9],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                },                   
            "500to900" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015, -0.013],
                    "a1" : [+0.5e-06, +2e-05],
                    "a2" : [-1.0e-9, -1.0e-10],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                },                    
            "600to1000" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015, -0.010],
                    "a1" : [+0.5e-06, +2e-05],
                    "a2" : [-1.0e-9, -1.0e-10],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                },        
            "700to1200" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015, -0.010],
                    "a1" : [+0.5e-06, +2e-05],
                    "a2" : [-1.0e-9, +1.0e-9],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                },               
            "700to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.04, -0.008],
                    "a1" : [0.0, +2.0e-04],
                    "a2" : [-1.0e-07, 0.0],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                }, 
            "800to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.04, -0.008],
                    "a1" : [0.0, +2.0e-04],
                    "a2" : [-1.0e-07, 0.0],
                    "a3" : [-1.0e-12, +1.0e-12],
                    },
                },               
            },
        }, # END EXP

    # POW
    "pow": {
        # degree
        "any": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [-4.2,-3.3],
                    "a1" : [-4.2e-04, -3.1e-04],
                    "a2" : [-2.2e-08, -1.8e-08],
                    "a3" : [+0.5e-11, +2.0e-11],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                }, 
            "400to800" : {                
                # parameter sets
                "default": {
                    "a0" : [-6.0,+6.0],
                    "a1" : [-1.0e-02, -1.0e-04],
                    "a2" : [+1.0e-08, +1.0e-06],
                    "a3" : [-1.0e-10, +2.0e-10],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                }, 
            "450to800" : {                
                # parameter sets
                "default": {
                    "a0" : [-6.0,+6.0],
                    "a1" : [-1.0e-02, -1.0e-04],
                    "a2" : [+1.0e-08, +1.0e-06],
                    "a3" : [-1.0e-10, +2.0e-10],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                }, 
            "500to900" : {                
                # parameter sets
                "default": {
                    "a0" : [-6.5,+6.5],
                    "a1" : [-1.0e-02, -1.0e-04],
                    "a2" : [+1.0e-09, +1.0e-06],
                    "a3" : [+0.5e-11, +2.0e-11],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                }, 
            "600to1000" : {                
                # parameter sets
                "default": {
                    "a0" : [-5.0,-3.0],
                    "a1" : [-5.0e-04, -1.0e-05],
                    "a2" : [-5.0e-07, -1.0e-08],
                    "a3" : [+0.5e-11, +2.0e-11],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                }, 
            "600to1300" : {                
                # parameter sets
                "default": {
                    "a0" : [-5.0,-3.0],
                    "a1" : [-5.0e-04, -1.0e-05],
                    "a2" : [-5.0e-07, -0.2e-08],
                    "a3" : [+0.5e-11, +2.0e-11],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                },
            "700to1200" : {                
                # parameter sets
                "default": {
                    "a0" : [-5.0,-3.0],
                    "a1" : [-5.0e-04, -1.0e-05],
                    "a2" : [-5.0e-07, -1.0e-08],
                    "a3" : [+0.5e-11, +2.0e-11],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                },  
            "700to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [-9.0,-3.0],
                    "a1" : [-5.0e-04, -1.0e-05],
                    "a2" : [-5.0e-07, -1.0e-09],
                    "a3" : [+0.5e-11, +2.0e-11],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                },  
            "800to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [-9.0,-3.0],
                    "a1" : [-1.0e-03, +1.0e-03],
                    "a2" : [-1.0e-07, +1.0e-07],
                    "a3" : [+0.5e-11, +2.0e-11],
                    "a4" : [-1.0e-12, +1.0e-12],
                    },
                },  
       
            },
        }, # END POW

    # POLYEXP
    "polyexp": {
        # degree
        "any": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-0.5e-02,-0.5e-03],
                    "a2" : [+1.0e-07,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-10],
                    },
                },
            "400to800" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-0.5e-02,-0.5e-03],
                    "a2" : [+1.0e-07,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-10],
                    },
                },
            "450to800" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-0.5e-02,-0.5e-03],
                    "a2" : [+1.0e-07,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-10],
                    },
                },
            "500to900" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-0.5e-02,-0.5e-03],
                    "a2" : [+1.0e-07,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-10],
                    },
                },
            "600to1000" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-0.5e-02,-0.5e-03],
                    "a2" : [+1.0e-07,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-10],
                    },
                },        
            "700to1200" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-0.5e-02,-0.5e-03],
                    "a2" : [+1.0e-07,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-10],
                    },
                },
            "700to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-1.0e-02,-0.5e-03],
                    "a2" : [+1.0e-08,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-8],
                    },
                },
            "800to1400" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [-1.0e-02,-0.5e-03],
                    "a2" : [+1.0e-08,+1.0e-05],
                    "a3" : [+1.0e-12,+1.0e-8],
                    },
                },
            },

        "deg1": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    },
                },        
            },

        "deg2": {
            # mass ranges
            "default" : {                
                # parameter sets
                "default": {
                    "a0" : [-0.015,-0.005],
                    "a1" : [+1.0e-07,+5.0e-05],
                    },
                },        
            },
        }, # END POLYEXP


   
    }
