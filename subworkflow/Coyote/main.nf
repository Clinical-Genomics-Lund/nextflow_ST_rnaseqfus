/*
Import modules according to the subworkflow of the RNA pipelines
*/

include { COYOTE } from '../../modules/coyote/main.nf'


workflow coyoteWorkflow {
    take:
        allFusCalls
        metaCoyote
        cronDir

    main:
        COYOTE (allFusCalls, metaCoyote, cronDir)
        
}