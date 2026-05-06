"use client";

import {
  Card,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
} from "@tremor/react";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";

interface EngagementType {
  type: string;
  useCases: number;
  eacv: number;
  eacvFormatted: string;
  attachRate: number;
  attachRateFormatted: string;
  topWorkloads: string;
  activity: string;
}

interface EngagementTypeTableProps {
  data: EngagementType[];
  loading?: boolean;
}

export function EngagementTypeTable({ data, loading }: EngagementTypeTableProps) {
  if (loading) {
    return (
      <Card className="ring-0">
        <div className="animate-pulse space-y-3">
          <div className="h-4 w-64 bg-crystalline-border rounded" />
          <div className="h-48 bg-crystalline-border rounded" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="ring-0">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-headline font-bold text-sm text-crystalline-text">
          PS Impact by Engagement Type
        </h3>
        <button className="flex items-center gap-1 text-xs text-crystalline-primary font-medium hover:underline">
          Detailed Report
          <ArrowTopRightOnSquareIcon className="w-3.5 h-3.5" />
        </button>
      </div>
      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell className="text-crystalline-muted text-xs">
              Engagement Type
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs text-right">
              Use Cases
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs text-right">
              EACV
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs text-right">
              Attach Rate
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">
              Top Workloads
            </TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">
              What We&apos;re Doing
            </TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6}>
                <p className="text-crystalline-muted text-center py-4 text-sm">
                  No engagement data
                </p>
              </TableCell>
            </TableRow>
          ) : (
            data.map((row) => (
              <TableRow key={row.type}>
                <TableCell className="text-xs font-medium">
                  {row.type}
                  {row.type !== "Implementation" &&
                    row.type !== "Advisory" &&
                    row.type !== "Proposing" &&
                    row.type !== "Support" &&
                    row.type !== "Resident" && (
                      <span className="text-crystalline-muted ml-1">*</span>
                    )}
                </TableCell>
                <TableCell className="text-xs text-right tabular-nums">
                  {row.useCases.toLocaleString()}
                </TableCell>
                <TableCell className="text-xs text-right tabular-nums font-medium">
                  {row.eacvFormatted}
                </TableCell>
                <TableCell className="text-xs text-right tabular-nums">
                  {row.attachRateFormatted}
                </TableCell>
                <TableCell className="text-xs text-crystalline-muted">
                  {row.topWorkloads}
                </TableCell>
                <TableCell className="text-xs text-crystalline-muted italic">
                  {row.activity}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </Card>
  );
}
