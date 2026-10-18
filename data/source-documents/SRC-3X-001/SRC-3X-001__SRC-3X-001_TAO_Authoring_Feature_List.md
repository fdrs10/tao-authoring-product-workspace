---
artifact_status: RECONSTRUCTED_FROM_USER_SUPPLIED_SOURCE
author: Dragos Ivan
date: 2026-09-11
origin: OAT Confluence / Product
scope: TAO 3.x Authoring
source_id: SRC-3X-001
source_type: Product Capability Baseline
status: ACTIVE
title: TAO Authoring - feature list
---

# TAO Authoring - feature list

This feature list can be used standalone as it is, or can be the basis
for a gap-analysis exercise against TAO Studio.

## Reference materials used

-   Item creation \| User Guide
-   Test assembly \| User Guide
-   Content banking \| User Guide
-   Product Requirements Document (PRD) \| Features

## 1. Item Authoring

  -----------------------------------------------------------------------
  Feature                             Feature description
  ----------------------------------- -----------------------------------
  Item creation & editing             Create items from scratch; edit
                                      existing items; save changes;
                                      configure identifier, title,
                                      instructions and other item
                                      properties

  Standard response interactions      Choice, Order, Associate, Match,
                                      Hottext, Gap Match, Slider,
                                      Extended Text, File Upload and
                                      Media interactions

  Inline interactions                 Inline Choice, Text Entry, End
                                      Attempt and other supported
                                      inline/block interaction types

  Graphical interactions              Hotspot, Select Point, Graphic
                                      Order, Graphic Associate and
                                      Graphic Gap Match

  Custom interactions (PCI)           Use Portable Custom Interactions
                                      and other installed/custom
                                      interaction types within items

  Rich-text authoring                 Create and format textual content,
                                      including headings, lists, tables,
                                      links and other rich-text elements

  Mathematical content                Insert and edit mathematical
                                      expressions within item content;
                                      MathML & LATeX support; Wiris
                                      MathType integration

  Images & media                      Insert and configure images, audio,
                                      video and other media assets within
                                      items

  Passages / shared stimuli           Insert and reuse passages/shared
                                      stimuli within authored items

  Response configuration & correct    Configure expected/correct
  answers                             responses and interaction-specific
                                      response properties

  Scoring & response processing       Configure match-correct scoring,
                                      mapped scoring and custom
                                      response-processing behaviour

  Feedback                            Configure feedback associated with
                                      responses and outcomes

  Item styling                        Configure item presentation using
                                      the Item Style Editor and
                                      applicable styling options

  Item source editing                 Directly inspect/edit the
                                      underlying item/QTI source

  Item preview                        Preview authored items before use;
                                      support both CurrentGen and NextGen
                                      preview experiences

  Item printing                       Produce a printable representation
                                      of an authored item

  Item language & writing direction   Configure item language and writing
                                      direction for
                                      multilingual/localized content
  -----------------------------------------------------------------------

## 2. Test authoring & assembly

  -----------------------------------------------------------------------
  Feature                             Feature description
  ----------------------------------- -----------------------------------
  Test creation & editing             Create tests from scratch; edit
                                      existing tests; configure test
                                      identity and general properties

  Test structure                      Build hierarchical assessments
                                      using Test → Test Part → Section →
                                      Item structures

  Test parts & sections management    Add, configure, rename/reorder and
                                      remove parts and sections

  Item placement & organization       Add multiple items to sections;
                                      remove, reorder and move items
                                      within the test structure

  Item selection                      Define which items are
                                      eligible/selected within test
                                      sections during the test
                                      execution/delivery

  Random item selection               Dynamically select a specified
                                      number of items from eligible item
                                      pools, during the test
                                      execution/delivery

  Ordering & shuffling                Configure fixed versus randomized
                                      ordering of applicable
                                      items/sections

  Navigation configuration            Configure linear/non-linear
                                      navigation

  Time limits                         Configure timing constraints at all
                                      levels of the test structure

  Test-taker tools configuration      Configure applicable tools made
                                      available during test delivery

  Test/part/section/item settings     Configure delivery-related
                                      behaviour at the different levels
                                      of the test hierarchy

  Scoring weights                     Configure weights associated with
                                      items/outcomes within the
                                      assessment

  Rubrics & instructions              Add instructional/rubric content at
                                      applicable levels of the test
                                      structure

  Categories                          Configure/use categories within
                                      test structures where supported

  Test-level outcome/scoring          Configure applicable test-level
  configuration                       scoring and outcome behaviour

  Test XML editing                    Inspect and directly edit the
                                      underlying test XML using the XML
                                      Editor

  Test preview                        Preview the complete assembled
                                      assessment before publication,
                                      using applicable preview
                                      environments

  Test printing                       Produce a printable representation
                                      of the assembled test
  -----------------------------------------------------------------------

## 3. Content banking & management

  -----------------------------------------------------------------------
  Feature                             Feature description
  ----------------------------------- -----------------------------------
  Hierarchical content organization   Organize content through TAO's
                                      hierarchical class/folder structure

  Item banking                        Store, browse, select and reuse
                                      assessment items

  Test banking                        Store, browse and manage reusable
                                      tests

  Asset banking / Asset Manager       Store and manage reusable
                                      images/media/assets independently
                                      from individual items

  Passage / shared stimulus           Store, manage and reuse
  management                          passages/shared stimuli

  Passage stylesheet management       Manage styling/stylesheet behaviour
                                      associated with reusable passages

  Resource class/folder management    Create and manage the
                                      classes/folders used to structure
                                      the content bank

  Resource copy & duplication         Copy or duplicate banked resources,
                                      including applicable handling of
                                      associated permissions/properties

  Resource movement                   Move resources between
                                      classes/folders

  Resource deletion                   Delete/remove resources from the
                                      bank

  Resource properties                 View and manage identity/properties
                                      associated with banked resources

  Item version history                Maintain a history of item
                                      revisions

  Version commit & restore            Explicitly commit revisions and
                                      restore previous item versions

  Item & test usage information       Identify usage/relationships of
                                      items and tests within assessment
                                      content

  Content preview                     Preview applicable banked resources
                                      directly from the
                                      content-management environment
                                      without entering the full authoring
                                      workflow

  Item statistics                     Access statistical information
                                      associated with banked items
  -----------------------------------------------------------------------

## 4. Metadata, search & governance

  -----------------------------------------------------------------------
  Feature                             Feature description
  ----------------------------------- -----------------------------------
  Custom metadata schemas             Define metadata properties/schema
                                      associated with content classes

  Metadata lists / controlled         Define reusable lists of allowed
  vocabularies                        metadata values

  Resource classification             Apply metadata/classification
                                      values to items and other
                                      applicable resources

  Basic content search                Locate resources within the content
                                      bank using basic identifying
                                      information

  Advanced Search                     Search/filter banked resources
                                      based on metadata and resource
                                      properties

  Compound search criteria            Combine criteria using Include all
                                      / Include any / Include none-style
                                      logic

  Hierarchy-scoped search             Search within applicable
                                      parts/classes of the content-bank
                                      hierarchy

  Item status & workflow              Manage content lifecycle/status,
                                      including Draft → Final and
                                      configurable/custom workflows

  Content access control (ACL)        Grant access to applicable
                                      folders/classes/resources

  Read/write permissions              Control read/write access to
                                      managed content

  Hierarchical permission management  Manage permissions in relation to
                                      the content-bank hierarchy

  Statistical metadata                Associate/import externally
                                      generated statistical analysis
                                      information with items
  -----------------------------------------------------------------------

## 5. Import, export & interoperability

  -----------------------------------------------------------------------
  Feature                             Feature description
  ----------------------------------- -----------------------------------
  QTI 2.x import                      Import standards-based QTI
                                      assessment packages, including QTI
                                      2.2

  QTI 2.x export                      Export applicable items/tests as
                                      QTI packages

  QTI 3 import                        Import QTI 3 assessment content

  QTI 3 export                        Export assessment content using QTI
                                      3

  CSV / tabular item import           Create/import structured assessment
                                      items from CSV/tabular files

  RDF import/export                   Exchange supported content using
                                      TAO's legacy RDF formats

  APIP import/export                  Exchange applicable APIP assessment
                                      packages

  Statistical metadata import         Import externally produced
                                      statistical-analysis data
                                      associated with items

  Assessment-content APIs             Programmatically import/export
                                      assessment content using TAO's Open
                                      APIs
  -----------------------------------------------------------------------

## 6. Publishing & delivery preparation

  -----------------------------------------------------------------------
  Feature                             Feature description
  ----------------------------------- -----------------------------------
  Test publishing                     Publish a completed/assembled test
                                      so that it becomes available for
                                      delivery

  Publishing to TAO Advance           Publish authored tests for use by
                                      the NextGen TAO Advance delivery
                                      environment

  Delivery creation from a test       Create a delivery based on an
                                      authored test

  Large QTI test publishing           Specialized publishing capability
                                      for particularly large QTI
                                      assessments
  -----------------------------------------------------------------------

## 7. Extensibility & specialized capabilities

  -----------------------------------------------------------------------
  Feature                             Feature description
  ----------------------------------- -----------------------------------
  Portable Custom Interaction (PCI)   Extend the standard QTI interaction
  extensibility                       set using Portable Custom
                                      Interactions

  Additional/custom PCIs              Deploy/use additional interaction
                                      implementations beyond the standard
                                      TAO interaction set

  Plugin / extension capability       Extend applicable TAO 3.x
                                      functionality through its
                                      plugin/extension architecture

  Open API extensibility              Integrate external
                                      content-management/authoring
                                      workflows through exposed APIs

  Remote Lists (specialized)          Integrate externally supplied
                                      lists; customer-specific capability
                                      originally developed for UDIR

  Booklets (specialized)              Generate/use specialized
                                      booklet-oriented assessment output;
                                      functionality associated with BOSA

  Customer-specific/custom authoring  Additional deployed PCIs or
  extensions (specialized)            authoring extensions that are not
                                      necessarily part of the generic TAO
                                      product baseline
  -----------------------------------------------------------------------
