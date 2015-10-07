/**
 (c) Mark Vismer, 2013

 A sample header file to convert. Demonstrates all the features of h2pyex.
*/
 
#ifndef SAMPLE_H
#define SAMPLE_H

#include "system.h"

/**
 @addtogroup sample Sample
 @{
*/


/** Defines the data format for the message. */
#pragma pack( push, 1) // Pack to 1 byte  for correct structure to byte array mapping
typedef struct {
    int8_t bi;
    uint8_t bu;
    
    int16_t di;
    uint16_t du;
    
    int32_t qi;
    uint32_t qu;
    
    float f;
    double dbl;
} Sample_StructDef_t;
#pragma pack( pop )


/* Not supported
struct Sample_StructDef_tag{
    int8_t bi;
    uint8_t bu;
    
    int16_t di;
    uint16_t du;
    
    int32_t qi;
    uint32_t qu;
    
    float f;
    double dbl;
} Sample_StructDef_t
typedef struct Sample_StructDef_t;
*/

// Array data types
typedef struct {
    int8_t bi[5];
    uint8_t bu[3];
    
    // A pre comment
    int16_t di[2]; //An inline comment
    uint16_t du;
    
    int32_t qi[0];
    uint32_t qu[1];
    
    float f[4];
    double dbl[3];
} Sample_StructDefArrays_t;


// Nested structs
typedef struct {    
    float32_t afloat; 
} Sample_NestC_t;

// Nested structs
typedef struct {    
    float32_t afloat; 
    Sample_NestC_t cnests;
} Sample_NestB_t;


// Message format for sending parameters into the motor controller for all motors.
typedef struct {
    Sample_NestB_t bnest; 
    double testdouble;
    Sample_NestC_t cnest;
    Sample_NestB_t bnests[2];
} Sample_NestA_t;


/**
 @} // End doxygen group
*/ 



#endif /* #ifdef SAMPLE_H */

