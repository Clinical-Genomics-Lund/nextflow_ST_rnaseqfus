/*
Import modules according to the subworkflow of the RNA pipelines
*/
include { FASTP } from '../../modules/fastp/main.nf'
include { SUBSAMPLE } from '../../modules/subsample/main.nf'

workflow subSampleWorkflow {
    take:
        sampleReads
        fileInfo
    main:
        // def input = readNumber.combine(sampleInfo)
        FASTP (fileInfo)
        SUBSAMPLE (sampleReads, FASTP.out.fq)

    emit:
        subSample = SUBSAMPLE.out
}