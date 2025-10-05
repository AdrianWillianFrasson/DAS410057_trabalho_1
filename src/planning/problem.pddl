(define (problem cafe-prob1)
    (:domain cafe)

    (:objects
        drink1 - drink-cold
        drink2 - drink-hot
    )

    (:init
        ;; Problem 1 ---------------------------------------
        (drink-ordered drink1)
        (drink-ordered drink2)

        ; Destinations
        (drink-destination drink1 table1)
        (drink-destination drink2 table1)

        ; Dirty tables
        (table-clean table1)
        (table-clean table2)
        ; (table-clean table3)
        ; (table-clean table4)

        ;; Constants (Do not change) -----------------------
        (robot-location waiter bar)

        (= (robot-speed waiter) 2)
        (= (robot-inventory-size waiter) 0)

        ; Time to clean dirty tables
        (= (time-clean table1) 2)
        (= (time-clean table2) 2)
        (= (time-clean table3) 4)
        (= (time-clean table4) 2)

        ; Distances between locations
        (= (distance bar bar) 0)
        (= (distance bar table1) 2)
        (= (distance bar table2) 2)
        (= (distance bar table3) 3)
        (= (distance bar table4) 3)

        (= (distance table1 bar) 2)
        (= (distance table1 table1) 0)
        (= (distance table1 table2) 1)
        (= (distance table1 table3) 1)
        (= (distance table1 table4) 1)

        (= (distance table2 bar) 2)
        (= (distance table2 table1) 1)
        (= (distance table2 table2) 0)
        (= (distance table2 table3) 1)
        (= (distance table2 table4) 1)

        (= (distance table3 bar) 3)
        (= (distance table3 table1) 1)
        (= (distance table3 table2) 1)
        (= (distance table3 table3) 0)
        (= (distance table3 table4) 1)

        (= (distance table4 bar) 3)
        (= (distance table4 table1) 1)
        (= (distance table4 table2) 1)
        (= (distance table4 table3) 1)
        (= (distance table4 table4) 0)
    )

    (:goal
        (and
            ;; All drinks delivered
            (drink-delivered drink1)
            (drink-delivered drink2)

            ;; Tables must be clean
            (table-clean table1)
            (table-clean table2)
            (table-clean table3)
            (table-clean table4)

            ;; Tray must be returned
            (not (robot-tray waiter))
        )
    )

    (:metric minimize
        (total-time)
    )
)