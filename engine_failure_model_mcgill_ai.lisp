

(clear-all)

(define-model engine_failure_model

(sgp :v nil :show-focus t :trace-detail low)
(sgp 
   :visual-attention-latency 0.0 ;default is 0.085
   :imaginal-delay 0.0 ;default is 0.2
)

(chunk-type checklist-procedure
   procedure-name
   help-level
   step
   phase
)

(chunk-type monitor-task
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

   (master-w-representation
      isa         aircraft-component-status-representation
      aircraft-component-name    master-w
      status    "0")

   (expertise-inference-representation
      isa      aircraft-component-status-representation
      aircraft-component-name    expertise-inference
      status    "NA"
   )
      
)

(goal-focus monitor-master-w)

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

;Check the current value of pilot control 0 = low control, 1 = high control
(p start-monitoring-expertise-inference
   =goal>
   isa      monitor-task
   phase    attend-expertise
==>
   =goal>
   isa      monitor-task
   monitored-parameter     expertise-inference
   phase    attend
)

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

(p no-alarm-detected ; NO ALARM DETECTED
   =goal>
	isa		monitor-task
   monitored-parameter     =monitored-parameter
	phase		action
   =imaginal>
	isa		   aircraft-component-status-representation
	aircraft-component-name		=monitored-parameter
	- status	   "1"
==>
   =goal>
	phase		attend-again
   =imaginal>
   isa      aircraft-component-status-representation
   aircraft-component-name    =monitored-parameter
)

(p no-inference-yet ;NO INFERENCE YET, BACK TO START MONITORING LOOP
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
)



)
