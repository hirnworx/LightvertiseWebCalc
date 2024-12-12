def lk_price(qcm, type, lkw):
    # Define the price table for ranges and prices
    price_table = [
        (1500, {"scheibe": {"einseitig": 760, "beitseitig": 1045}, "dk": {"einseitig": 1370, "beitseitig": 1580}}),
        (3000, {"scheibe": {"einseitig": 760, "beitseitig": 1045}, "dk": {"einseitig": 1370, "beitseitig": 1580}}),
        (4000, {"scheibe": {"einseitig": 532, "beitseitig": 730}, "dk": {"einseitig": 970, "beitseitig": 1115}}),
        (5000, {"scheibe": {"einseitig": 532, "beitseitig": 730}, "dk": {"einseitig": 970, "beitseitig": 1115}}),
        (6000, {"scheibe": {"einseitig": 456, "beitseitig": 620}, "dk": {"einseitig": 820, "beitseitig": 950}}),
        (7500, {"scheibe": {"einseitig": 408, "beitseitig": 560}, "dk": {"einseitig": 745, "beitseitig": 855}}),
        (10000, {"scheibe": {"einseitig": 360, "beitseitig": 495}, "dk": {"einseitig": 660, "beitseitig": 760}}),
        (12500, {"scheibe": {"einseitig": 340, "beitseitig": 475}, "dk": {"einseitig": 630, "beitseitig": 725}}),
        (15000, {"scheibe": {"einseitig": 332, "beitseitig": 460}, "dk": {"einseitig": 610, "beitseitig": 700}}),
        (17500, {"scheibe": {"einseitig": 316, "beitseitig": 440}, "dk": {"einseitig": 580, "beitseitig": 670}}),
        (20000, {"scheibe": {"einseitig": 308, "beitseitig": 425}, "dk": {"einseitig": 560, "beitseitig": 650}}),
        (30000, {"scheibe": {"einseitig": 304, "beitseitig": 415}, "dk": {"einseitig": 550, "beitseitig": 630}}),
        (40000, {"scheibe": {"einseitig": 280, "beitseitig": 385}, "dk": {"einseitig": 515, "beitseitig": 595}}),
        (50000, {"scheibe": {"einseitig": 268, "beitseitig": 370}, "dk": {"einseitig": 495, "beitseitig": 570}}),
        (59999, {"scheibe": {"einseitig": 260, "beitseitig": 360}, "dk": {"einseitig": 475, "beitseitig": 550}}),
        (75000, {"scheibe": {"einseitig": 252, "beitseitig": 350}, "dk": {"einseitig": 460, "beitseitig": 530}}),
        (100000, {"scheibe": {"einseitig": 244, "beitseitig": 340}, "dk": {"einseitig": 445, "beitseitig": 515}}),
        (125000, {"scheibe": {"einseitig": 236, "beitseitig": 330}, "dk": {"einseitig": 430, "beitseitig": 500}}),
        (150000, {"scheibe": {"einseitig": 228, "beitseitig": 320}, "dk": {"einseitig": 415, "beitseitig": 485}}),
        (200000, {"scheibe": {"einseitig": 220, "beitseitig": 310}, "dk": {"einseitig": 400, "beitseitig": 470}}),
    ]

    # Determine the price based on qcm and the ranges
    for max_qcm, prices in price_table:
        if qcm <= max_qcm:
            return prices.get(lkw, {}).get(type, 0)

    # Default return if no match found
    return 0
