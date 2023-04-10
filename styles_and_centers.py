styles = ['streets-v12',
          'outdoors-v12',
          'satellite-v9',
          'satellite-streets-v12',
          'navigation-day-v1',
          'navigation-night-v1',]


centers = ['22/672028/1464716/.7/.7',
           '21/336014/732358/.3/.3',
           '20/168007/366179/.15/.15',
           '19/84003/183089/.6/.6',
           '18/42001/91544/.85/.85',
           '17/21000/45772/.9/.3',
           '16/10500/22886/.4/.2',
           '15/5250/11443/.2/.1',
           '14/2625/5721/.07/.5',
           '13/1312/2860/.7/.5',
           '12/656/1430/.2/.3',
           '11/328/715/.1/.2',
           '10/164/357/.06/.6',
           '9/82/178/.8/.01',
           '8/41/89/.01/.4',
           '7/20/44/.5/.7',
           '6/10/22/.3/.2',]

tile_width = 512
tile_height = 512

tile_range = 16


def parse_center(center):
    center = center.split('/')
    print(center)
    return (int(center[0]), int(center[1]), int(center[2]), int(
        tile_width * float(center[3])), int(tile_height * float(center[4])))
