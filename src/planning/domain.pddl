(define (domain cafe)
    (:requirements :typing :durative-actions :numeric-fluents :negative-preconditions)

    (:types
        robot-barista robot-waiter - robot
        drink-cold drink-hot - drink
        table - location
        location drink robot
    )

    (:constants
        table1 table2 table3 table4 - table
        bar - location
        barista - robot-barista
        waiter - robot-waiter
    )

    (:predicates
        (drink-ordered ?d - drink);; Drinks ordered by clients
        (drink-prepared ?d - drink) ;; Drinks prepared on counter
        (drink-delivered ?d - drink) ;; Drinks delivered to tables
        (drink-destination ?d - drink ?t - table)
        (robot-busy ?r - robot)
        (robot-tray ?r - robot-waiter)
        (robot-location ?r - robot-waiter ?l - location)
        (robot-inventory ?r - robot-waiter ?d - drink)
        (table-clean ?t - table)
    )

    (:functions
        (time-clean ?t - table)
        (distance ?from - location ?to - location)
        (robot-speed ?r - robot-waiter)
        (robot-inventory-size ?r - robot-waiter)
    )

    (:durative-action prepare-drink-cold
        :parameters (?r - robot-barista ?d - drink-cold)
        :duration (= ?duration 3)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (drink-ordered ?d)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (drink-ordered ?d)))
            (at end (drink-prepared ?d))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action prepare-drink-hot
        :parameters (?r - robot-barista ?d - drink-hot)
        :duration (= ?duration 5)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (drink-ordered ?d)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (drink-ordered ?d)))
            (at end (drink-prepared ?d))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action move-robot
        :parameters (?r - robot-waiter ?from - location ?to - location)
        :duration (= ?duration (/ (distance ?from ?to) (robot-speed ?r)))
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (robot-location ?r ?from)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (robot-location ?r ?from)))
            (at end (robot-location ?r ?to))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action take-tray
        :parameters (?r - robot-waiter)
        :duration (= ?duration 0)
        :condition (and
            (at start (not (robot-busy ?r)))
            (over all (<= (robot-inventory-size ?r) 0))
            (over all (not (robot-tray ?r)))
            (over all (robot-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (assign (robot-speed ?r) 1))
            (at end (robot-tray ?r))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action return-tray
        :parameters (?r - robot-waiter)
        :duration (= ?duration 0)
        :condition (and
            (at start (not (robot-busy ?r)))
            (over all (<= (robot-inventory-size ?r) 0))
            (over all (robot-tray ?r))
            (over all (robot-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (assign (robot-speed ?r) 2))
            (at end (not (robot-tray ?r)))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action pickup-drink-gripper
        :parameters (?r - robot-waiter ?d - drink)
        :duration (= ?duration 1)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (drink-prepared ?d))
            (at start (< (robot-inventory-size ?r) 1))
            (over all (not (robot-tray ?r)))
            (over all (robot-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (drink-prepared ?d)))
            (at start (increase (robot-inventory-size ?r) 1))
            (at end (robot-inventory ?r ?d))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action pickup-drink-tray
        :parameters (?r - robot-waiter ?d - drink)
        :duration (= ?duration 1)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (drink-prepared ?d))
            (at start (< (robot-inventory-size ?r) 3))
            (over all (robot-tray ?r))
            (over all (robot-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (drink-prepared ?d)))
            (at start (increase (robot-inventory-size ?r) 1))
            (at end (robot-inventory ?r ?d))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action deliver-drink
        :parameters (?r - robot-waiter ?d - drink ?t - table)
        :duration (= ?duration 1)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (robot-inventory ?r ?d))
            (over all (table-clean ?t))
            (over all (drink-destination ?d ?t))
            (over all (robot-location ?r ?t)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (robot-inventory ?r ?d)))
            (at start (decrease (robot-inventory-size ?r) 1))
            (at end (drink-delivered ?d))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action clean-table
        :parameters (?r - robot-waiter ?t - table)
        :duration (= ?duration (time-clean ?t))
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (not (table-clean ?t)))
            (over all (not (robot-tray ?r)))
            (over all (<= (robot-inventory-size ?r) 0))
            (over all (robot-location ?r ?t)))
        :effect (and
            (at start (robot-busy ?r))
            (at end (table-clean ?t))
            (at end (not (robot-busy ?r))))
    )
)