(clear-all)

(define-model takeoff_model

(sgp :v nil :show-focus t :trace-detail low)
(sgp 
   :visual-attention-latency 0.085 ;default is 0.085
   :imaginal-delay 0.2 ;default is 0.2
)

(chunk-type checklist-procedure
   procedure-name
   help-level
   step
   phase
)

(chunk-type monitor-task
   previous-monitored-parameter
   monitored-parameter
   phase
)

(chunk-type  checklist-item-representation
	item-name
)

(chunk-type  aircraft-component-status-representation
	aircraft-component-name
	status
)

(define-chunks
   (pre-takeoff isa chunk)
   (attend isa chunk)
   (master-w isa chunk)
   (expertise-inference isa chunk)
   (encode isa chunk)
   (item-representation isa chunk)
   (type-value isa chunk)
   (start isa chunk)
   (attend-again isa chunk)
   (action isa chunk)
   (acknowledge-alarm isa chunk)
)

(add-dm	(checklist-goal
		isa 			checklist-procedure
		procedure-name	 	pre-takeoff
		step 			1
		phase			1
	)

   (monitor-master-w
      isa         monitor-task
      monitored-parameter  master-w
      phase       start)
   
   (monitor-start
      isa         monitor-task
      monitored-parameter  start-parameter
      phase       start)

   (master-w-representation
      isa         aircraft-component-status-representation
      aircraft-component-name    master-w
      status    "0")
)

(goal-focus monitor-start)

;;;;;;;;;;; PRODUCTION RULES ;;;;;;;;;;;

;First production;
(p start
   =goal>
   isa      monitor-task
   phase    start
==>
   =goal>
   phase    attend
)

(p attend-start-parameter
   =goal>
   isa      monitor-task
   monitored-parameter  start-parameter
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 370
   = screen-y 656
   =goal>
   phase    encode
)

(p attend-aviate-allocation-parameter
   =goal>
   isa      monitor-task
   monitored-parameter  aviate-allocation
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   = screen-x 369
   = screen-y 706
   =goal>
   phase    encode
)

(p attend-kias-parameter
   =goal>
   isa      monitor-task
   monitored-parameter  kias
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 370
   = screen-y 406
   =goal>
   phase    encode
)

(p attend-master-w
   =goal>
   isa      monitor-task
   monitored-parameter  master-w
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 360
   = screen-y 356
   =goal>
   phase    encode
)

(p attend-master-c
   =goal>
   isa      monitor-task
   monitored-parameter  master-c
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 440
   = screen-y 356
   =goal>
   phase    encode
)

(p attend-eicas
   =goal>
   isa      monitor-task
   monitored-parameter  eicas
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 540
   = screen-y 356
   =goal>
   phase    encode
)

(p attend-otw
   =goal>
   isa      monitor-task
   monitored-parameter  otw
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 540
   = screen-y 306
   =goal>
   phase    encode
)

(p encode-item
   =goal>
   isa      monitor-task
   phase    encode
   =visual-location>
   ?visual>
   state    free
==>
   +visual>
   isa      move-attention
   screen-pos  =visual-location
   =goal>
   phase    item-representation
)

(p encode-item-vr
   =goal>
   isa      monitor-task
   phase    encode-vr
   =visual-location>
   ?visual>
   state    free
==>
   +visual>
   isa      move-attention
   screen-pos  =visual-location
   =goal>
   phase    item-representation-vr
)

(p encode-item-save
   =goal>
   isa      monitor-task
   phase    encode
   ?visual>
   state    free
   ?visual-location>
   buffer   empty
==>
   +visual-location>
   isa      visual-location
   = screen-x 369
   = screen-y 706
   =goal>
   phase    encode
)

(p item-representation
   =goal>
   isa      monitor-task
   monitored-parameter =item
   phase    item-representation
   =visual>
   value    =status
   ?imaginal>
   state    free
==>
   +imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name   =item
   status   =status
   =goal>
   phase    action
   monitored-parameter  =item
)

(p item-representation-vr
   =goal>
   isa      monitor-task
   monitored-parameter =item
   phase    item-representation-vr
   =visual>
   value    =status
   ?imaginal>
   state    free
==>
   +imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name   =item
   status   =status
   =goal>
   phase    action-vr
   monitored-parameter  =item
)

(p not-started-yet ;not started yet, back to monitoring loop
   =goal>
	isa		monitor-task
   monitored-parameter     start-parameter
	phase		action
   =imaginal>
	isa		   aircraft-component-status-representation
	aircraft-component-name		start-parameter
	status	   "False"
==>
   =goal>
	phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    start-parameter
)

(p started ;started takeoff
   =goal>
	isa		monitor-task
   monitored-parameter     start-parameter
	phase		action
   =imaginal>
	isa		   aircraft-component-status-representation
	aircraft-component-name		start-parameter
	status	   "True"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      1
   =goal>
   isa monitor-task
   monitored-parameter     aviate-allocation
   phase    attend
)

(p briefing-package-no-received
   =goal>
   isa      monitor-task
   monitored-parameter  aviate-allocation
   phase    action
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    aviate-allocation
   status    "INIT"
==>
   =goal>
	phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    aviate-allocation
)

(p briefing-package-received-pilot-performer
   =goal>
   isa      monitor-task
   monitored-parameter  aviate-allocation
   phase    action
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    aviate-allocation
   status    "Pilot"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      2
   =goal>
   isa monitor-task
   monitored-parameter     kias
   phase    attend
)

(p briefing-package-received-TARS-performer
   =goal>
   isa      monitor-task
   monitored-parameter  aviate-allocation
   phase    action
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    aviate-allocation
   status    "TARS"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      3
)

(p vr-not-reached
   =goal>
   isa      monitor-task
   monitored-parameter  kias
   phase    action
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    kias
   - status    "vr"
==>
   =goal>
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-w
)

(p vr-reached
   =goal>
   isa      monitor-task
   monitored-parameter  kias
   phase    action
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    kias
   status    "vr"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      4
   =goal>
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-w
)

(p no-alarm-detected-master-w ; NO ALARM DETECTED
   =goal>
   isa		monitor-task
   monitored-parameter     master-w
   phase		action
   =imaginal>
   isa		   aircraft-component-status-representation
   aircraft-component-name		master-w
   - status	   "1"
==>
   =goal>
   phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-c
)

(p no-alarm-detected-master-c ; NO ALARM DETECTED
   =goal>
   isa		monitor-task
   monitored-parameter     master-c
   phase		action
   =imaginal>
   isa		   aircraft-component-status-representation
   aircraft-component-name		master-c
   - status	   "1"
==>
   =goal>
   phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    eicas
)

(p no-alarm-detected-eicas ; NO ALARM DETECTED
   =goal>
   isa		monitor-task
   monitored-parameter     eicas
   phase		action
   =imaginal>
   isa		   aircraft-component-status-representation
   aircraft-component-name		eicas
   - status	   "1"
==>
   =goal>
   phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    otw
)

(p birds-not-detected
   =goal>
   isa      monitor-task
   monitored-parameter  otw
   phase    action
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    otw
   status    "environment"
   ?manual>
   state    free
==>
   =goal>
   phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    kias
)

(p birds-detected
   =goal>
   isa      monitor-task
   monitored-parameter  otw
   phase    action
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    otw
   status    "birds"
   ?manual>
   state    free
==>
   =goal>
   phase		check-vr
)

(p check-vr
   =goal>
   isa      monitor-task
   phase    check-vr
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 370
   = screen-y 406
   =goal>
   phase    encode-vr
)

(p reject-takeoff
   =goal>
   isa      monitor-task
   phase    action-vr
   =imaginal>
   isa      aircraft-component-status-representation
   - status    "vr"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      5
)

(p take-issue-in-the-air
   =goal>
   isa      monitor-task
   phase    action-vr
   =imaginal>
   isa      aircraft-component-status-representation
   status    "vr"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      4
   =goal>
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-w
)

(p monitor-start-again
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    start-parameter
==>
   =goal>
   isa      monitor-task
   monitored-parameter     start-parameter
   phase    attend
)

(p monitor-kias-again
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    kias
==>
   =goal>
   isa      monitor-task
   monitored-parameter     kias
   phase    attend
)

(p monitor-master-w
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-w
==>
   =goal>
   isa      monitor-task
   monitored-parameter     master-w
   phase    attend
)

(p monitor-master-c
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-c
==>
   =goal>
   isa      monitor-task
   monitored-parameter     master-c
   phase    attend
)

(p monitor-eicas
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    eicas
==>
   =goal>
   isa      monitor-task
   monitored-parameter     eicas
   phase    attend
)

(p monitor-otw
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    otw
==>
   =goal>
   isa      monitor-task
   monitored-parameter     otw
   phase    attend
)


#| ;old engine failure stuff
(p start-monitoring-kias
   =goal>
   isa      monitor-task
   phase    attend-kias
==>
   =goal>
   isa      monitor-task
   monitored-parameter     kias
   phase    attend
)

(p start-monitoring-master-w
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    engine-fire-alarm
==>
   =goal>
   isa      monitor-task
   monitored-parameter     master-w
   phase    attend
)

(p start-monitoring-master-c
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-w
==>
   =goal>
   isa      monitor-task
   monitored-parameter     master-c
   phase    attend
)

(p start-monitoring-engine-fire-alarm
   =goal>
   isa      monitor-task
   phase    attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    master-c
==>
   =goal>
   isa      monitor-task
   monitored-parameter     engine-fire-alarm
   phase    attend
)


(p attend-master-w
   =goal>
   isa      monitor-task
   monitored-parameter  master-w
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 50
   <= screen-y 50
   =goal>
   phase    encode
)

(p attend-master-w-alternate
   =goal>
   isa      monitor-task
   monitored-parameter  master-w
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   <= screen-x 355
   <= screen-y 356
   =goal>
   phase    encode
)

(p attend-expertise-inference-alternate
   =goal>
   isa      monitor-task
   monitored-parameter  expertise-inference
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   = screen-x 505
   = screen-y 806
   =goal>
   phase    encode
)

(p attend-kias
   =goal>
   isa      monitor-task
   monitored-parameter  kias
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   = screen-x 355
   = screen-y 406
   =goal>
   phase    encode
)

(p attend-master-c-alternate
   =goal>
   isa      monitor-task
   monitored-parameter  master-c
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   = screen-x 405
   = screen-y 356
   =goal>
   phase    encode
)

(p attend-engine-fire-alarm-alternate
   =goal>
   isa      monitor-task
   monitored-parameter  engine-fire-alarm
   phase    attend
   ?visual>
   state    free
   ?imaginal>
   state    free
   ?manual>
   state    free
==>
   +visual-location>
   isa      visual-location
   = screen-x 705
   = screen-y 356
   =goal>
   phase    encode
) |#



;(p no-alarm-detected ; NO ALARM DETECTED
;   =goal>
;	isa		monitor-task
;   monitored-parameter     =monitored-parameter
;	phase		action
;   =imaginal>
;	isa		   aircraft-component-status-representation
;	aircraft-component-name		=monitored-parameter
;	- status	   "1"
;==>
;   =goal>
;	phase		attend-again
;  =imaginal>
;   isa      aircraft-component-status-representation
;   aircraft-component-name    =monitored-parameter
;)

#| (p no-inference-yet ;NO INFERENCE YET, BACK TO START MONITORING LOOP
   =goal>
	isa		monitor-task
   monitored-parameter     expertise-inference
	phase		action
   =imaginal>
	isa		   aircraft-component-status-representation
	aircraft-component-name		expertise-inference
	status	   "NA"
==>
   =goal>
	phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    expertise-inference
)

(p pilot-has-control ;INFERENCE MADE, PILOT HAS CONTROL
   =goal>
	isa		monitor-task
   monitored-parameter     expertise-inference
	phase		action
   =imaginal>
	isa		   aircraft-component-status-representation
	aircraft-component-name		expertise-inference
	status	   "1"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      1
   =goal>
	isa      checklist-procedure
   procedure-name       engine-failure-after-v1
   help-level           low
   phase                1
   step                 1
)

(p pilot-has-no-control ;INFERENCE MADE, PILOT HAS NO CONTROL
   =goal>
	isa		monitor-task
   monitored-parameter     expertise-inference
	phase		action
   =imaginal>
	isa		   aircraft-component-status-representation
	aircraft-component-name		expertise-inference
	- status	   "1"
   ?manual>
   state    free
==>
   +manual>
   cmd      press-key
   key      0
   =goal>
	isa      checklist-procedure
   procedure-name       engine-failure-after-v1
   help-level           high
   phase                1
   step                 1
)

(p detect-alarm-master-w ;ALARM DETECTED START ACTION
   =goal>
	isa		monitor-task
	phase		action
   =imaginal>
	isa		aircraft-component-status-representation
	aircraft-component-name		master-w
	status	"1"
   ?manual>
	state		free
==>
   +manual>
   cmd         press-key
   key         a
   =goal>
	phase		attend-kias
)
(p detect-alarm-master-c ;ALARM DETECTED START ACTION
   =goal>
	isa		monitor-task
	phase		action
   =imaginal>
	isa		aircraft-component-status-representation
	aircraft-component-name		master-c
	status	"1"
   ?manual>
	state		free
==>
   +manual>
   cmd         press-key
   key         b
   =goal>
	phase		attend-kias
)

(p detect-alarm-engine-fire ;ALARM DETECTED START ACTION
   =goal>
	isa		monitor-task
	phase		action
   =imaginal>
	isa		aircraft-component-status-representation
	aircraft-component-name		engine-fire-alarm
	status	"1"
   ?manual>
	state		free
==>
   +manual>
   cmd         press-key
   key         c
   =goal>
	phase		attend-kias
)

(p kias-above-v1
   =goal>
	isa		monitor-task
	phase		action
   =imaginal>
	isa		aircraft-component-status-representation
	aircraft-component-name		kias
	status	"1"
   ?manual>
   state      free
==>
   +manual>
   cmd         press-key
   key         p
   =goal>
   phase       attend-expertise
)

(p kias-below-v1
   =goal>
	isa		monitor-task
	phase		action
   =imaginal>
	isa		aircraft-component-status-representation
	aircraft-component-name		kias
	- status	   "1"
   ?manual>
   state      free
==>
   +manual>
   cmd         press-key
   key         m
   =goal>
	isa checklist-procedure
   procedure-name       engine-failure-below-v1
   phase                1
   step                 1
) |#
)
