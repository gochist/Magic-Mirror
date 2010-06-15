import logging

warn_msg = ["", #0
            "duplicated twit_id, %(twit_id)s.", #1
            ]

def warn(n, **dict):
    logging.warning("%05d:"%n+warn_msg[n]%dict)











def test():    
    warn(1, id=123)
    
if __name__ == "__main__":
    test()