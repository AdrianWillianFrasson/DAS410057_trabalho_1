(define (problem cafe-prob1)
    (:domain cafe)

    (:objects
        drink1 - drink-cold
        drink2 - drink-cold
        drink3 - drink-cold
        drink4 - drink-cold
        ; drink5 - drink-hot
        ; drink6 - drink-hot
        ; drink7 - drink-hot
        ; drink8 - drink-hot
        )

    (:init
        ;; Problem -----------------------------------------
        (drink-ordered drink1)
        (drink-ordered drink2)
        (drink-ordered drink3)
        (drink-ordered drink4)
        ; (drink-ordered drink5)
        ; (drink-ordered drink6)
        ; (drink-ordered drink7)
        ; (drink-ordered drink8)

        ; Destinations
        (drink-destination drink1 table1)
        (drink-destination drink2 table1)
        (drink-destination drink3 table1)
        (drink-destination drink4 table4)
        ; (drink-destination drink5 table3)
        ; (drink-destination drink6 table3)
        ; (drink-destination drink7 table3)
        ; (drink-destination drink8 table3)

        ; Clean tables
        (table-clean table1)
        ; (table-clean table2)
        (table-clean table3)
        (table-clean table4)

        ;; Constants (Do not change) -----------------------
        (waiter-location waiter1 table1)
        (waiter-location waiter2 table2)

        (= (waiter-speed waiter1) 2)
        (= (waiter-speed waiter2) 2)

        (= (waiter-inventory-size waiter1) 0)
        (= (waiter-inventory-size waiter2) 0)

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
            ;; All drinks finished
            (forall
                (?d - drink)
                (drink-finished ?d))

            ;; All tables clean
            (forall
                (?t - table)
                (table-clean ?t))

            ;; All trays returned
            (forall
                (?r - robot-waiter)
                (not (waiter-tray ?r)))
        )
    )

    (:metric minimize
        (total-time)
    )
)