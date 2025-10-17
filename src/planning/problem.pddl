(define (problem cafe-problema2)
    (:domain cafe)

    (:objects
        drink1 - drink-cold
        drink2 - drink-cold
        drink3 - drink-hot
        drink4 - drink-hot
    )

    (:init
        ; Bebidas marcadas como pedidas
        (drink-ordered drink1)
        (drink-ordered drink2)
        (drink-ordered drink3)
        (drink-ordered drink4)

        ; Destino das bebidas
        (drink-destination drink1 table3)
        (drink-destination drink2 table3)
        (drink-destination drink3 table3)
        (drink-destination drink4 table3)

        ; Mesas limpas ou sujas
        ; (table-clean table1) <-- Mesa suja
        (table-clean table2)
        (table-clean table3)
        (table-clean table4)

        ; Constantes
        (waiter-location waiter1 table1)
        (waiter-location waiter2 table2)

        (= (waiter-speed waiter1) 2)
        (= (waiter-speed waiter2) 2)

        (= (waiter-inventory-size waiter1) 0)
        (= (waiter-inventory-size waiter2) 0)

        ; Time to clean dirty tables
        (= (time-to-clean table1) 2)
        (= (time-to-clean table2) 2)
        (= (time-to-clean table3) 4)
        (= (time-to-clean table4) 2)

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
            ; Todos as bebidas terminadas
            (forall
                (?d - drink)
                (drink-finished ?d))

            ; Todas as mesas limpas
            (forall
                (?t - table)
                (table-clean ?t))

            ; Todos as bandejas devolvidas
            (forall
                (?r - robot-waiter)
                (not (waiter-tray ?r)))
        )
    )

    (:metric minimize
        (total-time)
    )
)