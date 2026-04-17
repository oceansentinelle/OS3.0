"use client"

import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn, formatConfidence, getConfidenceColor } from "@/lib/utils"
import { Bot, Clock, Database, Target } from "lucide-react"

interface IntentPreviewProps {
  agent: string
  objective: string
  sources: string[]
  duration: string
  confidence: number
  impact: string
  status?: 'pending' | 'validated' | 'corrected' | 'interrupted' | 'deferred'
  onValidate?: () => void
  onCorrect?: () => void
  onInterrupt?: () => void
  onDefer?: () => void
  className?: string
}

export function IntentPreview({
  agent,
  objective,
  sources,
  duration,
  confidence,
  impact,
  status = 'pending',
  onValidate,
  onCorrect,
  onInterrupt,
  onDefer,
  className,
}: IntentPreviewProps) {
  const statusBadges = {
    pending: <Badge variant="outline">En attente</Badge>,
    validated: <Badge variant="default" className="bg-normal-500">Validé</Badge>,
    corrected: <Badge variant="default" className="bg-info-500">Corrigé</Badge>,
    interrupted: <Badge variant="destructive">Interrompu</Badge>,
    deferred: <Badge variant="outline">Différé</Badge>,
  }

  return (
    <Card className={cn("border-l-4 border-l-brand-primary", className)}>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-brand-primary" />
            <CardTitle className="text-lg">Intention de l'Agent</CardTitle>
          </div>
          {statusBadges[status]}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Agent */}
        <div className="flex items-start gap-3">
          <div className="text-sm text-muted-foreground min-w-[80px]">Agent</div>
          <div className="text-sm font-mono">{agent}</div>
        </div>

        {/* Objective */}
        <div className="flex items-start gap-3">
          <div className="text-sm text-muted-foreground min-w-[80px] flex items-center gap-1">
            <Target className="h-4 w-4" />
            Objectif
          </div>
          <div className="text-sm font-medium">{objective}</div>
        </div>

        {/* Sources */}
        <div className="flex items-start gap-3">
          <div className="text-sm text-muted-foreground min-w-[80px] flex items-center gap-1">
            <Database className="h-4 w-4" />
            Sources
          </div>
          <div className="flex flex-wrap gap-2">
            {sources.map((source, index) => (
              <Badge key={index} variant="outline" className="font-normal">
                {source}
              </Badge>
            ))}
          </div>
        </div>

        {/* Duration & Confidence */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Durée estimée:</span>
            <span className="text-sm font-medium">{duration}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Confiance:</span>
            <span className={cn("text-sm font-semibold", getConfidenceColor(confidence))}>
              {formatConfidence(confidence)}
            </span>
          </div>
        </div>

        {/* Impact */}
        <div className="rounded-md bg-muted/50 p-3">
          <div className="text-xs font-medium text-muted-foreground mb-1">
            Impact attendu
          </div>
          <div className="text-sm">{impact}</div>
        </div>
      </CardContent>

      {status === 'pending' && (
        <CardFooter className="flex flex-wrap gap-2">
          <Button
            onClick={onValidate}
            className="touch-target"
            aria-label="Valider l'intention de l'agent"
          >
            Valider
          </Button>
          <Button
            variant="secondary"
            onClick={onCorrect}
            className="touch-target"
            aria-label="Corriger l'intention"
          >
            Corriger
          </Button>
          <Button
            variant="destructive"
            onClick={onInterrupt}
            className="touch-target"
            aria-label="Interrompre l'agent"
          >
            Interrompre
          </Button>
          <Button
            variant="ghost"
            onClick={onDefer}
            className="touch-target"
            aria-label="Différer l'action"
          >
            Différer
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}
