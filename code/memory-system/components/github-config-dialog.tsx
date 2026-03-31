'use client';

import { useState } from 'react';
import { GitHubConfig } from '@/lib/types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Github, Eye, EyeOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GitHubConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  config: GitHubConfig | null;
  onSave: (config: GitHubConfig) => void;
}

export function GitHubConfigDialog({
  open,
  onOpenChange,
  config,
  onSave,
}: GitHubConfigDialogProps) {
  const [owner, setOwner] = useState(config?.owner || '');
  const [repo, setRepo] = useState(config?.repo || '');
  const [branch, setBranch] = useState(config?.branch || 'main');
  const [token, setToken] = useState(config?.token || '');
  const [showToken, setShowToken] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!owner.trim()) {
      newErrors.owner = 'Repository owner is required';
    }
    if (!repo.trim()) {
      newErrors.repo = 'Repository name is required';
    }
    if (!branch.trim()) {
      newErrors.branch = 'Branch name is required';
    }
    if (!token.trim()) {
      newErrors.token = 'Personal access token is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validate()) return;

    onSave({
      owner: owner.trim(),
      repo: repo.trim(),
      branch: branch.trim() || 'main',
      token: token.trim(),
    });
    
    onOpenChange(false);
  };

  const handleClose = () => {
    // Reset to current config when closing
    setOwner(config?.owner || '');
    setRepo(config?.repo || '');
    setBranch(config?.branch || 'main');
    setToken(config?.token || '');
    setErrors({});
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-500/10">
              <Github className="h-5 w-5 text-red-500" />
            </div>
            <div>
              <DialogTitle className="text-xl">GitHub Integration</DialogTitle>
              <DialogDescription>
                Configure GitHub sync to backup and sync your memories.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <p className="text-sm text-amber-700 dark:text-amber-300">
              <strong>Note:</strong> Your GitHub token is stored locally in your browser. 
              Make sure to use a token with <code>repo</code> scope for private repositories.
            </p>
          </div>

          {/* Owner */}
          <div className="space-y-2">
            <Label htmlFor="owner">
              Repository Owner <span className="text-red-500">*</span>
            </Label>
            <Input
              id="owner"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              placeholder="e.g., username or organization"
              className={cn(
                errors.owner && "border-red-500 focus-visible:ring-red-500"
              )}
            />
            {errors.owner && (
              <p className="text-sm text-red-500">{errors.owner}</p>
            )}
          </div>

          {/* Repo */}
          <div className="space-y-2">
            <Label htmlFor="repo">
              Repository Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="repo"
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              placeholder="e.g., my-memory-repo"
              className={cn(
                errors.repo && "border-red-500 focus-visible:ring-red-500"
              )}
            />
            {errors.repo && (
              <p className="text-sm text-red-500">{errors.repo}</p>
            )}
          </div>

          {/* Branch */}
          <div className="space-y-2">
            <Label htmlFor="branch">
              Branch <span className="text-red-500">*</span>
            </Label>
            <Input
              id="branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="e.g., main"
              className={cn(
                errors.branch && "border-red-500 focus-visible:ring-red-500"
              )}
            />
            {errors.branch && (
              <p className="text-sm text-red-500">{errors.branch}</p>
            )}
          </div>

          {/* Token */}
          <div className="space-y-2">
            <Label htmlFor="token">
              Personal Access Token <span className="text-red-500">*</span>
            </Label>
            <div className="relative">
              <Input
                id="token"
                type={showToken ? 'text' : 'password'}
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                className={cn(
                  "pr-10",
                  errors.token && "border-red-500 focus-visible:ring-red-500"
                )}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowToken(!showToken)}
              >
                {showToken ? (
                  <EyeOff className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <Eye className="h-4 w-4 text-muted-foreground" />
                )}
              </Button>
            </div>
            {errors.token && (
              <p className="text-sm text-red-500">{errors.token}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Create a token at{' '}
              <a 
                href="https://github.com/settings/tokens" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-red-500 hover:underline"
              >
                github.com/settings/tokens
              </a>
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={handleClose}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="bg-red-500 hover:bg-red-600"
          >
            Save Configuration
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
