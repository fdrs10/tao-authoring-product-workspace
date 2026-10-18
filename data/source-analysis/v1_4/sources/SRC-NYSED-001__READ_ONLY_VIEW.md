# 3.x Features and Enhancements (NYSED)

NYSED In-person training internal debrief:

During the three-day event OAT team members identified the following feature enhancements or functionalities that are missing from TAO 3.x. Some of these appear to be easy fixes or developments that should be initiated to improve the usability for the customer.

Below is a list compiled by Julien, Jeff, Jimmy, and Dan.  Julien has arranged them into several potential epics for review and consideration.

UI:

The URL of NYSED’s authoring (https://nysed-author-ignite-us.prod.gcp-us.taocloud.org/) is consistent when working in the environment, but it changes when logging out or a timeout occurs. The logout page should remain in the same domain.
=> Technical investigation needed. Can it be fixed in the tenant configuration, or is it a bug?

All dates should be displayed in the American format (MM.DD.YYYY). Currently, it is in the European format (DD.MM.YYYY). We noticed the wrong date format for the item's last modified date, but all dates displayed should use the American format. The time zone should be EST (New York).
=> Estimation needed.

NYSED needs to be able to select multiple items in a folder in the item bank. For example, when performing an action and a dialog appears, such as moving items to a folder with different permissions, this is unusable.

=> Feasibility and estimation needed. UX input needed.

Given the amount of assets, NYSED needs to easily find where assets are used. This includes the usage of media in passages and items, and the usage of passages in items. This is similar to the usage of items in tests currently accessible through the Usage tab in the Item Bank.
=> Estimation needed. UX input needed.

NYSED branding will be needed. We didn’t clarify if changing the logo and color scheme would be enough.
=> Business analysis needed.

The user location within each one of the banks’ folder structures should be persisted across a working session, to avoid having to find your way to a specific folder every time you change your view. The folder structure should be collapsed only after you log out.
=> Feasibility and estimation needed.

Proper SME language should be used, instead of QTI terms that are sometimes rather technical and not so common among the assessment practitioners. For example, words like “schema,” "stimuli," etc. cause confusion when definitions are not provided.
=> UX input needed for wording.

Add explanations on how to populate CSV files for imports. They contain technical terms that are not easily understood by SMEs.
=> UX input needed for wording.

Metadata management:

Clarify the role of the "Alias" property. Eventually, either rename it, remove it, or hide it.
=> Find explanation from Product Team.

Clarify the meaning of the "label" icon on a metadata item. Currently, the tooltip says: "Expose the property value to create automated categories".
=> UX input needed for wording.

Clarify the tooltip message for the "Is statistical" property. “Is statistical” is not editable and requires data to be uploaded from another source.
=> UX input needed for wording.

Rename the "Manage schema" tab to "Manage Metadata".
=> UX review needed for wording.

The "File" type of metadata doesn’t work.
=> Technical estimation needed.

Since NYSED would like to use metadata to store item rationales and correct solutions, the Math editor must be added to the HTML-rich text editor on the metadata page.
=> Feasibility and estimation needed.

Preview:

A graphical, non-functional item preview in the Item Bank would make good use of all the blank space when selecting an item, similar to what exists currently for assets.
=> Feasibility and estimation needed. UX input needed.

In the History tab of the item bank, a preview of the item stored in each commit is more than desired. This would help users find which state to restore before changing the history. A simple click on the commit should be enough to display a preview of the item at the selected state.
=> Feasibility and estimation needed. UX input needed.

In the Test Authoring tool, a preview of items should be available when clicking either an item in the item bank, or an item in the Test Authoring main screen (test structure). Optimally, along the preview, a Go To button should allow the user to navigate to the selected item in the item bank.
=> Feasibility and estimation needed. UX input needed.

Search:

Search in item content based on partial matches, not on full text. The search must cover all the items within the folder tree selected in the advanced search. By default, the search box in the main item bank view searches the whole item bank.
=> Feasibility and estimation needed.

Allow the user to perform bulk actions on multiple search results (move, delete, export at least).
=> Feasibility and estimation needed.

Access control:

When using access control in the Item/Test/Asset banks, all the elements without Read access should be hidden/removed from the tree structure, instead displaying the red lock icon. This would ease the navigation by focusing only on reachable content. On the other hand, all the elements with Read-only access should remain with the yellow lock icon.
=> Estimation needed.

The Read-only access (yellow lock) seems not to work consistently on items (it is still possible to open an item in the Authoring tool).
=> Check whether saving is possible before creating a ticket.

"Lock Out Message" is inconsistent.
=> Clarification needed from Jeffrey.

Workflow:

NYSED uses each item in a single test. When an item is included in a test, it should be marked/hidden/deactivated in the Item Bank. This is a specific requirement of NYSED, not as common across customers. This could be worked around if the usage in a test is a state in the workflow. Therefore, if we make a development, it should be activated by a feature flag. The data gathered for the item Usage in tests can be leveraged here.
=> Business analysis and estimation needed.

Each subject matter could have slightly different workflows. A suggested solution was to use a folder-based approach, since we didn’t start implementing real, configurable workflows.
=> Business analysis needed to understand if the folder-based approach addresses NYSED’s needs.

Additional observations not captured above:

.csv files for importing info into TAO need to have a tab added that includes an explanation of the column headings and what they represent.

Sourcing - the authors need to provide the source of a specific question/item. Clarify requirement

URLs

pages from reference books
