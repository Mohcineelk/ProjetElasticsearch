# ############################################################################################################ #
#                                 Programme : network                                                          #
#                                                                                                              #
#                                 Dernière modification : 10/03/2021                                           #
#                                                                                                              #
#                                 Réalisé par : EL KHADIMI Mohcine / SLIM Malik                                #
#                                                                                                              #                                                                                                              #
#                                                                                                              #
#                                                                                                              #
# ############################################################################################################ #

from elasticsearch import Elasticsearch 


es = Elasticsearch([{'host':'localhost','port':9200}])

#création de l'index network 
es.indices.create(index="network")

#dictionnaire contenant le mapping de l'index
mapping = {
            "properties":{
                "myNodeId":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "myParentId":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "packetTime":{
                    "type":"date",
                    "format" : "yyyy-MM-dd HH:mm:ss"
                },
                "dbTime":{
                    "type":"date",
                    "format" : "yyyy-MM-dd HH:mm:ss"
                },
                "messageType":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "nodeType":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "extAddr":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "shortAddr":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "softVersion":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "channelMask":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "panId":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "workingChannel":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "parentShortAddr":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "boardType":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "sensorsSize":{
                    "type":"text",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                },
                "Coord":{
                    "type":"geo_point",
                    "fields" : {
                        "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                }
            }
        }

#application du mapping à l'index network
es.indices.put_mapping(index="network",body=mapping)