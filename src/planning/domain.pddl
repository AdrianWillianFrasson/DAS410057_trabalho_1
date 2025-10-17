(define (domain cafe)
    (:requirements :typing :durative-actions :numeric-fluents :negative-preconditions :equality :disjunctive-preconditions)

    (:types
        robot-barista robot-waiter - robot
        drink-cold drink-hot - drink
        table - location
    )

    (:constants
        table1 table2 table3 table4 - table
        bar - location
        barista - robot-barista
        waiter1 waiter2 - robot-waiter
    )

    (:predicates
        (drink-ordered ?d - drink)
        (drink-prepared ?d - drink)
        (drink-delivered ?d - drink)
        (drink-finished ?d - drink)
        (drink-destination ?d - drink ?t - table)
        (drink-still-hot ?d - drink)
        (drink-is-hot ?d - drink)
        (robot-busy ?r - robot)
        (waiter-tray ?r - robot-waiter)
        (waiter-location ?r - robot-waiter ?l - location)
        (waiter-inventory ?r - robot-waiter ?d - drink)
        (waiter-assigned ?r - robot-waiter ?t - table)
        (table-clean ?t - table)
    )

    (:functions
        (time-to-clean ?t - table)
        (distance ?from - location ?to - location)
        (waiter-speed ?r - robot-waiter)
        (waiter-inventory-size ?r - robot-waiter)
        (hot-time-left ?d - drink)
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
            (at end (drink-is-hot ?d))
            (at end (assign (hot-time-left ?d) 4))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action hot-drink-cooling
        :parameters (?d - drink-hot)
        :duration (= ?duration 4)
        :condition (and
            (at start (not (drink-ordered ?d)))
            (at start (not (drink-delivered ?d)))
            (at start (not (drink-finished ?d)))
        )
        :effect (and
            (at start (drink-still-hot ?d))
            (at end (decrease (hot-time-left ?d) 4)))

    )

    (:durative-action move-robot
        :parameters (?r - robot-waiter ?from - location ?to - location)
        :duration (= ?duration (/ (distance ?from ?to) (waiter-speed ?r)))
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (waiter-location ?r ?from))
            (at start (not (and (= ?to bar)
                        (exists
                            (?o - robot-waiter)
                            (and (not (= ?o ?r)) (waiter-location ?o bar)))))))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (waiter-location ?r ?from)))
            (at end (waiter-location ?r ?to))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action take-tray
        :parameters (?r - robot-waiter)
        :duration (= ?duration 0)
        :condition (and
            (at start (not (robot-busy ?r)))
            (over all (<= (waiter-inventory-size ?r) 0))
            (over all (not (waiter-tray ?r)))
            (over all (waiter-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (assign (waiter-speed ?r) 1))
            (at end (waiter-tray ?r))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action return-tray
        :parameters (?r - robot-waiter)
        :duration (= ?duration 0)
        :condition (and
            (at start (not (robot-busy ?r)))
            (over all (<= (waiter-inventory-size ?r) 0))
            (over all (waiter-tray ?r))
            (over all (waiter-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (assign (waiter-speed ?r) 2))
            (at end (not (waiter-tray ?r)))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action pickup-drink-gripper
        :parameters (?r - robot-waiter ?d - drink)
        :duration (= ?duration 0.1)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (drink-prepared ?d))
            (at start (< (waiter-inventory-size ?r) 1))
            (over all (not (waiter-tray ?r)))
            (over all (waiter-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (drink-prepared ?d)))
            (at start (increase (waiter-inventory-size ?r) 1))
            (at end (waiter-inventory ?r ?d))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action pickup-drink-tray
        :parameters (?r - robot-waiter ?d - drink)
        :duration (= ?duration 0.1)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (drink-prepared ?d))
            (at start (< (waiter-inventory-size ?r) 3))
            (over all (waiter-tray ?r))
            (over all (waiter-location ?r bar)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (drink-prepared ?d)))
            (at start (increase (waiter-inventory-size ?r) 1))
            (at end (waiter-inventory ?r ?d))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action deliver-drink
        :parameters (?r - robot-waiter ?d - drink ?t - table)
        :duration (= ?duration 0.1)
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (waiter-inventory ?r ?d))
            (at start (not (and (drink-is-hot ?d) (not (drink-still-hot ?d)))))
            (at start (not (and (drink-is-hot ?d) (not (> (hot-time-left ?d) 0)))))
            (at start (or (waiter-assigned ?r ?t) (not (exists
                            (?o - robot-waiter)
                            (waiter-assigned ?o ?t)))))
            (over all (table-clean ?t))
            (over all (waiter-location ?r ?t))
            (over all (drink-destination ?d ?t)))
        :effect (and
            (at start (robot-busy ?r))
            (at start (not (waiter-inventory ?r ?d)))
            (at start (decrease (waiter-inventory-size ?r) 1))
            (at end (drink-delivered ?d))
            (at end (waiter-assigned ?r ?t))
            (at end (not (robot-busy ?r))))
    )

    (:durative-action finish-drink
        :parameters (?d - drink ?t - table)
        :duration (= ?duration 4)
        :condition (and
            (at start (drink-delivered ?d))
            (over all (drink-destination ?d ?t)))
        :effect (and
            (at start (not (drink-delivered ?d)))
            (at end (drink-finished ?d))
            (at end (not (table-clean ?t))))
    )

    (:durative-action clean-table
        :parameters (?r - robot-waiter ?t - table)
        :duration (= ?duration (time-to-clean ?t))
        :condition (and
            (at start (not (robot-busy ?r)))
            (at start (not (table-clean ?t)))
            (over all (not (waiter-tray ?r)))
            (over all (<= (waiter-inventory-size ?r) 0))
            (over all (waiter-location ?r ?t))
            (over all (not (exists
                        (?d - drink)
                        (and (drink-destination ?d ?t) (not (drink-finished ?d)))))))
        :effect (and
            (at start (robot-busy ?r))
            (at end (table-clean ?t))
            (at end (not (robot-busy ?r))))
    )
)