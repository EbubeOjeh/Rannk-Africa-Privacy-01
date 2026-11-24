import { createContext, useContext } from 'react';

/**
 * Null on the live public site. Inside the Website editor's live preview it
 * holds { page, draft, activeSection, onFocus } so previewed pages render the
 * unsaved draft and become click-to-edit.
 */
export const EditContext = createContext(null);

export const useEditContext = () => useContext(EditContext);
