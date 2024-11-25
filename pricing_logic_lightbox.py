def lk_price(qcm, type, lkw):
    if qcm < 1500:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 950
            elif type == "beitseitig":
                return 1045
        elif lkw == 'dk':
            if type == "einseitig":
                return 1370
            elif type == "beitseitig":
                return 1580
    elif qcm < 3000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 950
            elif type == "beitseitig":
                return 1045
        elif lkw == 'dk':
            if type == "einseitig":
                return 1370
            elif type == "beitseitig":
                return 1580
    elif qcm < 4000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 665
            elif type == "beitseitig":
                return 730
        elif lkw == 'dk':
            if type == "einseitig":
                return 970
            elif type == "beitseitig":
                return 1115
    elif qcm < 5000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 665
            elif type == "beitseitig":
                return 730
        elif lkw == 'dk':
            if type == "einseitig":
                return 970
            elif type == "beitseitig":
                return 1115
    elif qcm < 6000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 570
            elif type == "beitseitig":
                return 620
        elif lkw == 'dk':
            if type == "einseitig":
                return 820
            elif type == "beitseitig":
                return 950
    elif qcm < 7500:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 510
            elif type == "beitseitig":
                return 560
        elif lkw == 'dk':
            if type == "einseitig":
                return 745
            elif type == "beitseitig":
                return 855
    elif qcm < 10000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 450
            elif type == "beitseitig":
                return 495
        elif lkw == 'dk':
            if type == "einseitig":
                return 660
            elif type == "beitseitig":
                return 760
    elif qcm < 12500:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 425
            elif type == "beitseitig":
                return 475
        elif lkw == 'dk':
            if type == "einseitig":
                return 630
            elif type == "beitseitig":
                return 725
    elif qcm < 15000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 415
            elif type == "beitseitig":
                return 460
        elif lkw == 'dk':
            if type == "einseitig":
                return 610
            elif type == "beitseitig":
                return 700
    elif qcm < 17500:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 395
            elif type == "beitseitig":
                return 440
        elif lkw == 'dk':
            if type == "einseitig":
                return 580
            elif type == "beitseitig":
                return 670
    elif qcm < 20000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 385
            elif type == "beitseitig":
                return 425
        elif lkw == 'dk':
            if type == "einseitig":
                return 560
            elif type == "beitseitig":
                return 650
    elif qcm < 30000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 380
            elif type == "beitseitig":
                return 415
        elif lkw == 'dk':
            if type == "einseitig":
                return 550
            elif type == "beitseitig":
                return 630
    elif qcm < 40000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 350
            elif type == "beitseitig":
                return 385
        elif lkw == 'dk':
            if type == "einseitig":
                return 515
            elif type == "beitseitig":
                return 595
    elif qcm < 50000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 335
            elif type == "beitseitig":
                return 370
        elif lkw == 'dk':
            if type == "einseitig":
                return 495
            elif type == "beitseitig":
                return 570
    elif qcm < 59999:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 325
            elif type == "beitseitig":
                return 360
        elif lkw == 'dk':
            if type == "einseitig":
                return 475
            elif type == "beitseitig":
                return 550
    elif qcm >= 60000:
        if lkw == 'scheibe':
            if type == "einseitig":
                return 315
            elif type == "beitseitig":
                return 350
        elif lkw == 'dk':
            if type == "einseitig":
                return 460
            elif type == "beitseitig":
                return 530
    return 0
