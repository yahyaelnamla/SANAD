"use client";

import {
  Archive,
  ArchiveRestore,
  Download,
  FolderOpen,
  Pencil,
  Tag,
  Trash2,
} from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { ApiClientError } from "@/services/apiClient";
import {
  deleteQuery,
  exportQueryMarkdown,
  updateQueryMetadata,
} from "@/services/queryService";
import { useConversationStore } from "@/store/conversationStore";
import type { QueryListItem } from "@/types/query";

interface HistoryQueryActionsProps {
  item: QueryListItem;
  onUpdated: () => void;
}

export function HistoryQueryActions({ item, onUpdated }: HistoryQueryActionsProps) {
  const { t } = useTranslations();
  const { accessToken } = useAuth();
  const bumpHistory = useConversationStore((s) => s.bumpHistory);
  const removePinned = useConversationStore((s) => s.removePinned);
  const [busy, setBusy] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [titleDraft, setTitleDraft] = useState(item.display_title ?? item.question);
  const [folderDraft, setFolderDraft] = useState(item.folder ?? "");
  const [tagsDraft, setTagsDraft] = useState((item.tags ?? []).join(", "));

  const runAction = async (action: string, fn: () => Promise<void>) => {
    if (!accessToken || busy) return;
    setBusy(action);
    try {
      await fn();
      bumpHistory();
      onUpdated();
    } catch (err) {
      console.error(err instanceof ApiClientError ? err.message : err);
    } finally {
      setBusy(null);
    }
  };

  const handleRename = async () => {
    await runAction("rename", async () => {
      await updateQueryMetadata(item.query_id, accessToken!, {
        display_title: titleDraft.trim() || null,
      });
      setEditing(false);
    });
  };

  const handleArchiveToggle = async () => {
    await runAction("archive", async () => {
      await updateQueryMetadata(item.query_id, accessToken!, {
        archived: !item.archived,
      });
    });
  };

  const handleDelete = async () => {
    if (!window.confirm(t("history.deleteConfirm"))) return;
    await runAction("delete", async () => {
      await deleteQuery(item.query_id, accessToken!);
      removePinned([item.query_id]);
    });
  };

  const handleExport = async () => {
    await runAction("export", async () => {
      const exported = await exportQueryMarkdown(item.query_id, accessToken!);
      const blob = new Blob([exported.content], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = exported.filename;
      anchor.click();
      URL.revokeObjectURL(url);
    });
  };

  const handleSaveMeta = async () => {
    await runAction("meta", async () => {
      await updateQueryMetadata(item.query_id, accessToken!, {
        folder: folderDraft.trim() || "",
        tags: tagsDraft
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      });
      setEditing(false);
    });
  };

  if (editing) {
    return (
      <div className="mt-3 space-y-2 rounded-xl border border-border/50 bg-background/40 p-3">
        <label className="block space-y-1 text-xs">
          <span className="text-muted-foreground">{t("history.rename")}</span>
          <Input value={titleDraft} onChange={(e) => setTitleDraft(e.target.value)} />
        </label>
        <label className="block space-y-1 text-xs">
          <span className="text-muted-foreground">{t("history.folder")}</span>
          <Input value={folderDraft} onChange={(e) => setFolderDraft(e.target.value)} />
        </label>
        <label className="block space-y-1 text-xs">
          <span className="text-muted-foreground">{t("history.tags")}</span>
          <Input
            value={tagsDraft}
            onChange={(e) => setTagsDraft(e.target.value)}
            placeholder={t("history.tagsPlaceholder")}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <Button type="button" size="sm" onClick={() => void handleRename()} disabled={!!busy}>
            {t("history.saveRename")}
          </Button>
          <Button type="button" size="sm" variant="outline" onClick={() => void handleSaveMeta()} disabled={!!busy}>
            {t("history.saveMeta")}
          </Button>
          <Button type="button" size="sm" variant="ghost" onClick={() => setEditing(false)}>
            {t("admin.cancel")}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-1 pt-1">
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-8 gap-1 px-2 text-xs"
        onClick={() => setEditing(true)}
        aria-label={t("history.rename")}
      >
        <Pencil className="h-3.5 w-3.5" />
        {t("history.rename")}
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-8 gap-1 px-2 text-xs"
        onClick={() => void handleArchiveToggle()}
        disabled={!!busy}
        aria-label={item.archived ? t("history.unarchive") : t("history.archive")}
      >
        {item.archived ? (
          <ArchiveRestore className="h-3.5 w-3.5" />
        ) : (
          <Archive className="h-3.5 w-3.5" />
        )}
        {item.archived ? t("history.unarchive") : t("history.archive")}
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-8 gap-1 px-2 text-xs"
        onClick={() => void handleExport()}
        disabled={!!busy}
        aria-label={t("history.export")}
      >
        <Download className="h-3.5 w-3.5" />
        {t("history.export")}
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-8 gap-1 px-2 text-xs text-destructive hover:text-destructive"
        onClick={() => void handleDelete()}
        disabled={!!busy}
        aria-label={t("history.delete")}
      >
        <Trash2 className="h-3.5 w-3.5" />
        {t("history.delete")}
      </Button>
      {item.folder && (
        <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-1 text-[10px] text-muted-foreground">
          <FolderOpen className="h-3 w-3" />
          {item.folder}
        </span>
      )}
      {(item.tags ?? []).map((tag) => (
        <span
          key={tag}
          className="inline-flex items-center gap-1 rounded-full bg-cyan-500/10 px-2 py-1 text-[10px] text-cyan-300"
        >
          <Tag className="h-3 w-3" />
          {tag}
        </span>
      ))}
    </div>
  );
}
