/*
Import modules according to the subworkflow of the RNA pipelines
*/

include { STARFUSION_FUSCALL } from '../../../modules/starfusion/main.nf'

workflow starFusionWorkflow {
    take:
        pairEnd 
        starRef
        readsInfo

    main:
        if (pairEnd) {
            STARFUSION_FUSCALL ( starRef, readsInfo)
        }
    emit:
        fusion = STARFUSION_FUSCALL.out

}