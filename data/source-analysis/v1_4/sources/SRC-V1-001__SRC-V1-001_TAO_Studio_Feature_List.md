---
artifact_status: RECONSTRUCTED_FROM_USER_SUPPLIED_SOURCE
author: Dragos Ivan
date: 2026-09-11
origin: OAT Confluence / Product
scope: TAO Studio V1 / Authoring
source_id: SRC-V1-001
source_type: Product Capability Baseline
status: ACTIVE
title: TAO Studio - feature list
---

# TAO Studio - feature list

This feature list can be used standalone as it is, or can be the basis
for a gap-analysis exercise against TAO Authoring.

## Reference materials used

-   TAO3.x-Studio.pdf
-   tao-studio-sales-capability-map.pdf
-   module_9_generation.zip
-   module_8_conversion.zip
-   module_7_editor.zip
-   module_6_library_characteristics.zip
-   module_5_search_filters.zip
-   module_4_import_export.zip
-   module_3_taxonomy_setup.zip
-   module_2_user_preferences.zip
-   module_1_dashboard.zip
-   module_10_assembly.zip

## 1. Item Authoring

  -----------------------------------------------------------------------
  Feature                 Description             Confidence
  ----------------------- ----------------------- -----------------------
  Item creation & editing Create questions from   HIGH
                          scratch; edit existing  
                          QTI questions;          
                          configure question      
                          title and identifier;   
                          save changes and manage 
                          unsaved editing         
                          sessions                

  Standard response       Choice, Order,          HIGH
  interactions            Associate, Match,       
                          Hottext, Gap Match,     
                          Slider, Extended Text,  
                          File Upload, Media and  
                          other supported         
                          standard interactions   

  Inline interactions     Inline Choice, Text     HIGH
                          Entry, End Attempt and  
                          other supported inline  
                          interaction types       

  Graphical interactions  Hotspot, Select Point,  HIGH
                          Graphic Order, Graphic  
                          Associate and Graphic   
                          Gap Match               

  Rich-text authoring     Create and format       HIGH
                          textual content using   
                          the embedded QTI        
                          editor, including       
                          common text-formatting  
                          and structural elements 

  Mathematical content    Insert and edit         HIGH
                          mathematical            
                          expressions, including  
                          MathML-based            
                          mathematical content    

  Images & media          Insert and configure    MEDIUM
                          supported images,       
                          audio, video and other  
                          media within questions  

  Response configuration  Configure               HIGH
  & correct answers       expected/correct        
                          responses and           
                          interaction-specific    
                          response properties     

  Scoring & response      Configure applicable    HIGH
  processing              scoring and             
                          response-processing     
                          behaviour               

  Feedback                Configure supported     MEDIUM
                          feedback associated     
                          with responses/outcomes 

  Item styling            Configure question      MEDIUM
                          presentation through    
                          the embedded Style      
                          Editor and applicable   
                          styling/layout controls 

  Item preview            Preview questions       HIGH
                          before use, including   
                          library previews of QTI 
                          content                 

  Item printing           Produce a               HIGH
                          print-oriented          
                          representation of the   
                          current question        
  -----------------------------------------------------------------------

## 2. Test authoring & assembly

  ------------------------------------------------------------------------
  Feature                  Description             Confidence
  ------------------------ ----------------------- -----------------------
  Test creation & editing  Create tests from       HIGH
                           scratch or edit         
                           existing eligible tests 
                           using Studio's embedded 
                           test editor             

  Test structure           Build structured        HIGH
                           assessments using the   
                           hierarchy supported by  
                           the test editor and     
                           Studio assembly         
                           workflows               

  Test parts & sections    Add, configure and      HIGH
  management               organize applicable     
                           test parts and sections 

  Item placement &         Add questions to        MEDIUM
  organization             sections; remove,       
                           reorder and organize    
                           questions within a test 

  Item selection           Define which questions  HIGH
                           are used within test    
                           sections                

  Random item selection    Select a specified      HIGH
                           number of questions     
                           randomly from an        
                           eligible question set   
                           or filtered library     
                           pool                    

  Ordering & shuffling     Configure applicable    HIGH
                           fixed/randomized        
                           ordering and shuffling  
                           behaviour               

  Navigation configuration Configure applicable    HIGH
                           test navigation         
                           behaviour through the   
                           embedded test editor    

  Time limits              Configure applicable    HIGH
                           timing constraints      
                           through the embedded    
                           test editor             

  Test-taker tools         Configure applicable    MEDIUM
  configuration            tools made available    
                           during test delivery    

  Test/part/section/item   Configure applicable    HIGH
  settings                 behaviour at different  
                           levels of the test      
                           hierarchy               

  Scoring weights          Configure applicable    MEDIUM
                           weights associated with 
                           questions/outcomes      

  Rubrics & instructions   Add applicable          MEDIUM
                           instructional/rubric    
                           content within the test 
                           structure               

  Categories               Configure/use           MEDIUM
                           applicable QTI          
                           categories within test  
                           structures              

  Test-level               Configure applicable    MEDIUM
  outcome/scoring          test-level scoring and  
  configuration            outcome behaviour       

  Test preview             Preview assembled or    HIGH
                           edited tests before     
                           export/publication      

  Taxonomy-driven item     Build section question  HIGH
  pools                    pools dynamically from  
                           Library content         
                           matching specified      
                           taxonomy/tag criteria   
  ------------------------------------------------------------------------

## 3. Content banking & management

  -----------------------------------------------------------------------
  Feature                 Description             Confidence
  ----------------------- ----------------------- -----------------------
  Content Library         Centrally store and     HIGH
                          browse source           
                          documents, study        
                          materials, questions,   
                          tests, and other        
                          supported content       

  Item banking            Store, browse, preview, HIGH
                          edit, select and reuse  
                          assessment questions    

  Test banking            Store, browse, preview, HIGH
                          edit and reuse tests    

  Asset / source material Store and manage source HIGH
  management              files, study materials  
                          and supported           
                          media/content assets    
                          independently from      
                          individual questions    

  Resource properties     View resource identity, HIGH
                          status, access scope,   
                          content type, format,   
                          size, source, quality   
                          setting,                
                          creation/update dates   
                          and generated summary   

  Resource deletion       Delete individual or    HIGH
                          multiple resources from 
                          the Library             

  Resource download       Download source or      HIGH
                          generated resources     
                          from the Library        

  Bulk content operations Select multiple Library HIGH
                          resources and perform   
                          applicable export,      
                          conversion, tagging,    
                          download,               
                          authoring-send and      
                          deletion operations     

  Content relationships & Track Origin Document,  HIGH
  provenance              Related Documents,      
                          Derived Files and       
                          Project Usage           
                          relationships between   
                          source and              
                          generated/converted     
                          content                 

  Content preview         Preview supported       HIGH
                          source documents,       
                          questions, tests,       
                          stimuli and other       
                          Library resources       

  Task monitoring         Monitor conversion,     HIGH
                          generation, import and  
                          export processing       
                          activities              
  -----------------------------------------------------------------------

## 4. Metadata, search & governance

  -----------------------------------------------------------------------
  Feature                 Description             Confidence
  ----------------------- ----------------------- -----------------------
  Custom metadata schemas Configure categories    HIGH
                          and metadata applicable 
                          to different Studio     
                          content/document types  

  Metadata lists /        Define reusable List    HIGH
  controlled vocabularies categories with         
                          controlled metadata/tag 
                          values                  

  Hierarchical taxonomies Define hierarchical     HIGH
                          metadata structures     
                          such as Subject → Unit  
                          → Topic                 

  Open-value metadata     Define categories that  HIGH
                          permit open/free-form   
                          metadata values         

  Resource classification Apply categories and    HIGH
                          tags to applicable      
                          Library resources       

  Content-type-specific   Associate different     HIGH
  metadata                metadata/category       
                          configurations with     
                          questions, tests, study 
                          materials and other     
                          document types          

  Basic content search    Locate Library          HIGH
                          resources using         
                          identifying information 
                          such as filenames and   
                          tags                    

  Advanced Search         Search across           HIGH
                          filenames, metadata,    
                          summaries and extracted 
                          resource content        

  Semantic search         Retrieve resources      HIGH
                          based on semantic       
                          similarity to           
                          natural-language search 
                          terms, not only exact   
                          keyword matches         

  Content match context   Display matching        HIGH
                          content fragments       
                          explaining why a        
                          resource matched a      
                          content-aware search    

  Taxonomy filtering      Filter Library          HIGH
                          resources using         
                          configured categories   
                          and tags                

  Compound search         Combine search text,    HIGH
  criteria                multiple categories and 
                          tags to progressively   
                          refine Library results  

  Category counts         Display dynamic counts  HIGH
                          of matching Library     
                          resources for available 
                          metadata                
                          categories/values       

  Saved filters           Save reusable           HIGH
                          combinations of         
                          taxonomy/category       
                          filters and apply them  
                          to Library views        

  AI-assisted tagging     Generate metadata/tag   HIGH
                          suggestions for         
                          uploaded, converted or  
                          generated resources     

  AI tag review           Accept or reject        HIGH
                          AI-generated tag        
                          suggestions before they 
                          become confirmed        
                          metadata                

  AI tagging              Configure AI tagging    HIGH
  configuration           plans/prompts and       
                          determine applicable    
                          metadata categories     

  Project-specific        Override/configure      HIGH
  metadata configuration  category assignments    
                          for individual          
                          conversion/generation   
                          projects where          
                          supported               
  -----------------------------------------------------------------------

## 5. Import, export & interoperability

  -----------------------------------------------------------------------
  Feature                 Description             Confidence
  ----------------------- ----------------------- -----------------------
  QTI 2.x import          Import supported QTI    HIGH
                          2.x packages, including 
                          QTI 2.2 content         

  QTI 2.x export          Export applicable       HIGH
                          questions/tests as QTI  
                          2.2 packages            

  QTI 3 import            Import supported QTI 3  HIGH
                          assessment content      

  QTI 3 export            Export applicable       HIGH
                          assessment content as   
                          QTI 3.0 packages        

  CSV / tabular item      Upload structured CSV   LOW
  import                  question data for       
                          conversion into         
                          reusable assessment     
                          questions/tests         

  Document/source import  Upload PDF, DOCX and    HIGH
                          other supported         
                          source/exam documents   
                          for storage or          
                          conversion              

  Study-material import   Upload PDF, DOCX, SCORM HIGH
                          and other supported     
                          reference/study         
                          materials for           
                          AI-assisted generation  

  Booklet export          Export supported        MEDIUM
                          questions/tests into    
                          booklet-oriented        
                          outputs                 

  DOCX export             Produce editable DOCX   MEDIUM
                          booklet output from     
                          supported assessment    
                          content                 

  PDF export              Produce fixed-layout    MEDIUM
                          PDF booklet output from 
                          supported assessment    
                          content                 

  QTI conformance         Validate applicable     HIGH
  validation              assessment content      
                          against QTI 3.0 and QTI 
                          2.2 structural          
                          requirements and expose 
                          Valid/Pending/Invalid   
                          status                  
  -----------------------------------------------------------------------

## 6. Publishing & delivery preparation

  -----------------------------------------------------------------------
  Feature                 Description             Confidence
  ----------------------- ----------------------- -----------------------
  Publishing to TAO       Send supported          HIGH
  Authoring               Studio-authored or      
                          generated assessment    
                          content to a connected  
                          TAO Authoring           
                          environment             

  Target folder selection Select an applicable    HIGH
                          destination in TAO      
                          Authoring when          
                          publishing Studio       
                          content                 

  Metadata publishing     Transfer applicable     HIGH
                          Studio metadata         
                          alongside content when  
                          publishing to TAO       
                          Authoring               
  -----------------------------------------------------------------------

## 7. Extensibility & specialized capabilities

  -----------------------------------------------------------------------
  Feature                 Description             Confidence
  ----------------------- ----------------------- -----------------------
  Booklets (specialized)  Generate                HIGH
                          booklet-oriented        
                          assessment outputs      
                          using Studio's          
                          supported booklet       
                          workflow                

  -----------------------------------------------------------------------

## 8. AI-assisted content creation

  -----------------------------------------------------------------------
  Feature                 Description             Confidence
  ----------------------- ----------------------- -----------------------
  AI-assisted full-test   Convert an existing     HIGH
  conversion              assessment into a       
                          structured digital test 

  Source-to-output review Review source material  HIGH
                          alongside converted     
                          assessment content      

  Question generation     Create projects for     HIGH
  projects                generating assessment   
                          questions from          
                          source/study material   

  AI-assisted question    Generate new assessment HIGH
  generation              questions based on      
                          supplied source         
                          material and generation 
                          instructions            

  AI-assisted full-test   Generate a complete     HIGH
  generation              assessment based on     
                          supplied source         
                          material and            
                          requirements            

  Source-grounded         Ground generated        HIGH
  generation              assessment content in   
                          uploaded                
                          study/reference         
                          material                

  Generation guidance     Provide additional      HIGH
                          instructions that guide 
                          an individual           
                          content-generation      
                          process                 

  Conversion guidance     Provide additional      HIGH
                          instructions that guide 
                          an individual           
                          content-conversion      
                          process                 

  Output quality levels   Configure supported     HIGH
                          processing/quality      
                          levels for AI           
                          generation and          
                          conversion              

  Per-run quality         Override applicable     HIGH
  override                default quality         
                          settings for an         
                          individual              
                          generation/conversion   
                          run                     

  Question quality        Evaluate generated      HIGH
  evaluation              questions against       
                          configured quality      
                          criteria                

  Test quality evaluation Evaluate generated      HIGH
                          tests against           
                          configured quality      
                          criteria                

  Asset quality           Evaluate applicable     HIGH
  evaluation              assets against          
                          configured quality      
                          criteria                

  Configurable evaluation Configure criteria used HIGH
  criteria                by Studio when          
                          evaluating              
                          generated/converted     
                          content                 

  Item quality traits     Evaluate applicable     HIGH
                          item-quality            
                          characteristics through 
                          Studio's quality        
                          evaluation mechanisms   

  AI-assisted metadata    Generate metadata/tag   HIGH
  generation              suggestions as part of  
                          applicable              
                          generation/conversion   
                          workflows               

  Generated-content       Review generated        HIGH
  review                  questions/tests and     
                          associated quality      
                          information before      
                          subsequent use          
  -----------------------------------------------------------------------
