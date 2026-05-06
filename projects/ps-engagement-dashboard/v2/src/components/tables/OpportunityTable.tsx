"use client";

import {
  Card,
  Badge,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
} from "@tremor/react";

interface Opportunity {
  account: string;
  useCase: string;
  stage: string;
  eacv: number;
  eacvFormatted: string;
  pattern: string;
}

interface OpportunityTableProps {
  data: Opportunity[];
  total: number;
  loading?: boolean;
}

export function OpportunityTable({ data, total, loading }: OpportunityTableProps) {
  if (loading) {
    return (
      <Card className="ring-0">
        <div className="animate-pulse space-y-3">
          <div className="h-4 w-48 bg-crystalline-border rounded" />
          <div className="h-32 bg-crystalline-border rounded" />
        </div>
      </Card>
    );
  }

  const stageBadgeColor = (stage: string) => {
    if (stage === "Pipeline" || stage === "Scoping") return "blue" as const;
    if (stage === "Proposal") return "amber" as const;
    if (stage === "Unengaged") return "gray" as const;
    return "cyan" as const;
  };

  return (
    <Card className="ring-0">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="font-headline font-bold text-sm text-crystalline-text">
            Engagement Opportunity
          </h3>
          <Badge color="blue" size="sm">
            {total.toLocaleString()} Active Leads
          </Badge>
        </div>
        <button className="text-xs text-crystalline-primary font-semibold border border-crystalline-primary rounded-lg px-3 py-1.5 hover:bg-crystalline-primary hover:text-white transition-colors">
          Target Focus
        </button>
      </div>
      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell className="text-crystalline-muted text-xs">
              Account
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">
              Use Case
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">
              Stage
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs text-right">
              EACV
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">
              PS Pattern
            </TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5}>
                <p className="text-crystalline-muted text-center py-4 text-sm">
                  No opportunities found
                </p>
              </TableCell>
            </TableRow>
          ) : (
            data.map((opp, i) => (
              <TableRow key={i}>
                <TableCell className="text-xs font-medium">
                  {opp.account}
                </TableCell>
                <TableCell className="text-xs">{opp.useCase}</TableCell>
                <TableCell>
                  <Badge color={stageBadgeColor(opp.stage)} size="xs">
                    {opp.stage}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs text-right tabular-nums font-medium">
                  {opp.eacvFormatted}
                </TableCell>
                <TableCell className="text-xs text-crystalline-muted italic">
                  {opp.pattern}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </Card>
  );
}
