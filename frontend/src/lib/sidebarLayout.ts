/** Shared sidebar width tokens — keep skeleton and live sidebar aligned to prevent layout shift. */

export const SIDEBAR_WIDTH_EXPANDED = "w-72";
export const SIDEBAR_WIDTH_COLLAPSED = "w-[72px]";

export function sidebarWidthClass(collapsed: boolean): string {
  return collapsed ? SIDEBAR_WIDTH_COLLAPSED : SIDEBAR_WIDTH_EXPANDED;
}
