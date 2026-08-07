"use client"

import * as React from "react"

import api from "@/services/api"
import { useRouter } from "next/navigation";
import type { PullRequest } from "@/types"
import Link from "next/link"

import {
  Eye,
  ExternalLink,
  Columns3Icon,
  ChevronDownIcon,
  Search,
  ChevronsLeftIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronsRightIcon,
  User,
  GitBranch,
  Shield,
  Building2,
  CalendarDays,
  CheckCircle2,
} from "lucide-react"

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
} from "@tanstack/react-table"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"



const getStatusVariant = (state: string) => {
  switch (state.toLowerCase()) {
    case "open":
      return "default"

    case "closed":
      return "secondary"

    default:
      return "outline"
  }
}

const getScoreColorClass = (score: number) => {
  if (score >= 90) return "bg-green-600 text-white"
  if (score >= 75) return "bg-yellow-500 text-white"
  return "bg-red-500 text-white"
}

const getSeverityVariant = (severity: string) => {
  switch (severity.toLowerCase()) {
    case "high":
      return "destructive"

    case "medium":
      return "secondary"

    case "low":
      return "outline"

    default:
      return "outline"
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  })
}

interface DataTableProps {
  repositoryId?: string;
  limit?: number;
}

interface DataTableProps {
  repositoryId?: string;
  limit?: number;
}

export function DataTable({
  repositoryId,
  limit,
}: DataTableProps)  {
  const [data, setData] = React.useState<PullRequest[]>([])
  const [loading, setLoading] = React.useState(true)
  const [selectedPR, setSelectedPR] = React.useState<PullRequest | null>(null)
  const [drawerOpen, setDrawerOpen] = React.useState(false)
  const router = useRouter();

  React.useEffect(() => {
    const fetchPRs = async () => {
      try {
        const endpoint = "/pull-requests";

const res = await api.get(endpoint);
        let prs = res.data;
        if (repositoryId) {
  prs = prs.filter(
    (pr: PullRequest) =>
      String(pr.repository.id) === String(repositoryId)
  );
}

if (limit) {
  prs = prs.slice(0, limit);
}

setData(prs);
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchPRs()
  }, [repositoryId, limit])

  const columns: ColumnDef<PullRequest>[] = [
    {
      accessorKey: "pr_number",
      header: "PR",
      cell: ({ row }) => (
        <div className="font-medium">
          #{row.original.pr_number}
        </div>
      ),
    },

    {
      accessorKey: "title",
      header: "Title",
      cell: ({ row }) => (
        <div className="max-auto-sm truncate font-medium">
          {row.original.title}
        </div>
      ),
    },

    {
      accessorKey: "repository",
      header: "Repository",
      cell: ({ row }) => (
        <div className="flex flex-col">
          <span className="font-medium">
            {row.original.repository.name}
          </span>

          <span className="text-xs text-muted-foreground">
            {row.original.repository.owner}
          </span>
        </div>
      ),
    },

    {
      accessorKey: "author",
      header: "Author",
      cell: ({ row }) => (
        <div>{row.original.author}</div>
      ),
    },

    {
      accessorKey: "state",
      header: "Status",
      cell: ({ row }) => (
        <Badge
          variant={getStatusVariant(row.original.state)}
          className={
            row.original.state === "open"
              ? "bg-green-500 text-white"
              : ""
          }
        >
          {row.original.state}
        </Badge>
      ),
    },

    {
      id: "score",
      header: "AI Score",
      cell: ({ row }) => {
        const review = row.original.latest_review

        if (!review) {
          return (
            <span className="text-muted-foreground">
              —
            </span>
          )
        }

        return (
          <Badge
            className={
              review.final_score >= 90
                ? "bg-green-600"

                : review.final_score >= 75
                ? "bg-yellow-500"

                : "bg-red-500"
            }
          >
            {review.final_score}/100
          </Badge>
        )
      },
    },

    {
      id: "security",
      header: "Security",
      cell: ({ row }) => {
        const review = row.original.latest_review

        return review ? review.security_score : "—"
      },
    },

    {
      id: "style",
      header: "Style",
      cell: ({ row }) => {
        const review = row.original.latest_review

        return review ? review.style_score : "—"
      },
    },

    {
      id: "architecture",
      header: "Architecture",
      cell: ({ row }) => {
        const review = row.original.latest_review

        return review ? review.architecture_score : "—"
      },
    },

    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-2">

          <Link href={`/pull-requests/${row.original.id}`}>
  <Button
    variant="outline"
    size="sm"
    onClick={(e) => e.stopPropagation()}
  >
    <Eye className="mr-2 h-4 w-4" />
    View
  </Button>
</Link>

          <Button
            variant="secondary"
            size="icon"
            onClick={(e) => {
              e.stopPropagation()
              window.open(
                `https://github.com/${row.original.repository.full_name}/pull/${row.original.pr_number}`,
                "_blank"
              )
            }}
          ><ExternalLink className="h-4 w-4" />
            
          </Button>

        </div>
      ),
    },
  ]

  const [rowSelection, setRowSelection] = React.useState({})
  const [globalFilter, setGlobalFilter] = React.useState("")
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [pagination, setPagination] = React.useState({
    pageIndex: 0,
    pageSize: 10,
  })


  const filteredData = React.useMemo(() => {
    if (!globalFilter) return data

    const search = globalFilter.toLowerCase()

    return data.filter((pr) =>
      pr.title.toLowerCase().includes(search) ||
      pr.author.toLowerCase().includes(search) ||
      pr.repository.name.toLowerCase().includes(search)
    )
  }, [data, globalFilter])

  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      sorting,
      columnVisibility,
      rowSelection,
      columnFilters,
      pagination,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onPaginationChange: setPagination,
    onGlobalFilterChange: setGlobalFilter,

    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  

  return (
    <>
      <Tabs
        defaultValue="all"
        className="w-full flex-col justify-start gap-6"
      >
      <div className="flex flex-col gap-4 px-4 lg:flex-row lg:items-center lg:justify-between">
        <TabsList>
          <TabsTrigger value="all">All PRs</TabsTrigger>
        </TabsList>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Columns3Icon data-icon="inline-start" />
                Columns
                <ChevronDownIcon data-icon="inline-end" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-32">
              {table
                .getAllColumns()
                .filter(
                  (column) =>
                    typeof column.accessorFn !== "undefined" &&
                    column.getCanHide()
                )
                .map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                      key={column.id}
                      className="capitalize"
                      checked={column.getIsVisible()}
                      onCheckedChange={(value) =>
                        column.toggleVisibility(!!value)
                      }
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  )
                })}
            </DropdownMenuContent>
          </DropdownMenu>
          <div className="flex items-center gap-3">

    <div className="relative">

        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />

        <Input
            placeholder="Search Pull Requests..."
            className="pl-9 w-72"
            value={globalFilter}
            onChange={(e)=>setGlobalFilter(e.target.value)}
        />

    </div>

</div>
        </div>
      </div>
      <TabsContent
        value="all"
        className="relative w-full flex flex-col gap-4"
      >
        <div className="w-full overflow-x-auto rounded-lg border">
          {loading ? (
            <div className="flex h-60 items-center justify-center">
              Loading Pull Requests...
            </div>
          ) : (
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <TableHead key={header.id}>
                        {header.isPlaceholder
                          ? null
                          : flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                      </TableHead>
                    ))}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows.length ? (
                  table.getRowModel().rows.map((row) => (
                    <TableRow
                      key={row.id}
                      data-state={row.getIsSelected() && "selected"}
                      className="cursor-pointer hover:bg-muted/50 transition"
                      onClick={() => {
                        router.push(`/pull-requests/${row.original.id}`)
                      }}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length}
                      className="text-center py-10"
                    >
                      No Pull Requests Found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </div>
        <div className="flex items-center justify-between px-4">
          <div className="flex w-full items-center gap-8 lg:w-fit">
            <div className="hidden items-center gap-2 lg:flex">
              <Label htmlFor="rows-per-page" className="text-sm font-medium">
                Rows per page
              </Label>
              <Select
                value={`${table.getState().pagination.pageSize}`}
                onValueChange={(value) => {
                  table.setPageSize(Number(value))
                }}
              >
                <SelectTrigger size="sm" className="w-20" id="rows-per-page">
                  <SelectValue
                    placeholder={table.getState().pagination.pageSize}
                  />
                </SelectTrigger>
                <SelectContent side="top">
                  <SelectGroup>
                    {[10, 20, 30, 40, 50].map((pageSize) => (
                      <SelectItem key={pageSize} value={`${pageSize}`}>
                        {pageSize}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div className="text-sm text-muted-foreground">
              Showing {table.getRowModel().rows.length} of {data.length} Pull
              Requests
            </div>
            <div className="ml-auto flex items-center gap-2 lg:ml-0">
              <Button
                variant="outline"
                className="hidden h-8 w-8 p-0 lg:flex"
                onClick={() => table.setPageIndex(0)}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="sr-only">Go to first page</span>
                <ChevronsLeftIcon
                />
              </Button>
              <Button
                variant="outline"
                className="size-8"
                size="icon"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="sr-only">Go to previous page</span>
                <ChevronLeftIcon
                />
              </Button>
              <Button
                variant="outline"
                className="size-8"
                size="icon"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                <span className="sr-only">Go to next page</span>
                <ChevronRightIcon
                />
              </Button>
              <Button
                variant="outline"
                className="hidden size-8 lg:flex"
                size="icon"
                onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                disabled={!table.getCanNextPage()}
              >
                <span className="sr-only">Go to last page</span>
                <ChevronsRightIcon
                />
              </Button>
            </div>
          </div>
        </div>
      </TabsContent>
      </Tabs>

      <ReviewDrawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        pr={selectedPR}
      />
    </>
  )
}

function ReviewDrawer({
  open,
  onOpenChange,
  pr,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  pr: PullRequest | null
}) {
  if (!pr) return null

  const review = pr.latest_review

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent className="max-h-[90vh]">

        <DrawerHeader>

          <DrawerTitle>
            Pull Request #{pr.pr_number}
          </DrawerTitle>

          <DrawerDescription>
            {pr.title}
          </DrawerDescription>

        </DrawerHeader>

        <div className="overflow-y-auto px-6 pb-6 space-y-6">

          {/* Repository */}

          <div>

            <h3 className="flex items-center gap-2 font-semibold">
              <GitBranch className="h-4 w-4" />
              Repository
            </h3>

            <p>
              <span className="text-muted-foreground">
                {pr.repository.owner}
              </span>
              {" / "}
              <span className="font-medium">{pr.repository.name}</span>
            </p>

          </div>

          {/* Author */}

          <div>

            <h3 className="flex items-center gap-2 font-semibold">
              <User className="h-4 w-4" />
              Author
            </h3>

            <p>{pr.author}</p>

          </div>

          {/* Branch */}

          <div className="grid grid-cols-2 gap-4">

            <div>

              <h3 className="flex items-center gap-2 font-semibold">
                <GitBranch className="h-4 w-4" />
                Base Branch
              </h3>

              <p>{pr.base_branch}</p>

            </div>

            <div>

              <h3 className="flex items-center gap-2 font-semibold">
                <GitBranch className="h-4 w-4" />
                Head Branch
              </h3>

              <p>{pr.head_branch}</p>

            </div>

          </div>

          {!review ? (

            <div className="rounded-lg border p-6 text-center">

              No AI Review Available

            </div>

          ) : (

            <>

              <div>

                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-lg font-semibold">
                    AI Review Scores
                  </h2>

                  {review.created_at && (
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                      <CalendarDays className="h-4 w-4" />
                      Reviewed {formatDate(review.created_at)}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

                  <div
                    className={`rounded-lg border p-4 ${getScoreColorClass(
                      review.final_score
                    )}`}
                  >

                    <p className="text-sm opacity-90">
                      Overall
                    </p>

                    <h2 className="text-3xl font-bold">
                      {review.final_score}
                    </h2>

                  </div>

                  <div
                    className={`rounded-lg border p-4 ${getScoreColorClass(
                      review.security_score
                    )}`}
                  >

                    <p className="flex items-center gap-1 text-sm opacity-90">
                      <Shield className="h-3.5 w-3.5" />
                      Security
                    </p>

                    <h2 className="text-3xl font-bold">
                      {review.security_score}
                    </h2>

                  </div>

                  <div
                    className={`rounded-lg border p-4 ${getScoreColorClass(
                      review.style_score
                    )}`}
                  >

                    <p className="text-sm opacity-90">
                      Style
                    </p>

                    <h2 className="text-3xl font-bold">
                      {review.style_score}
                    </h2>

                  </div>

                  <div
                    className={`rounded-lg border p-4 ${getScoreColorClass(
                      review.architecture_score
                    )}`}
                  >

                    <p className="flex items-center gap-1 text-sm opacity-90">
                      <Building2 className="h-3.5 w-3.5" />
                      Architecture
                    </p>

                    <h2 className="text-3xl font-bold">
                      {review.architecture_score}
                    </h2>

                  </div>

                </div>

              </div>

              <div>

                <h2 className="text-lg font-semibold">

                  AI Summary

                </h2>

                <div className="mt-3 rounded-lg border p-4 whitespace-pre-wrap">

                  {review.summary}

                </div>

              </div>

              <div>

                <h2 className="text-lg font-semibold mb-4">

                  Files Reviewed

                </h2>

                <div className="space-y-6">

                  {review.agent_output.map((file, index) => (

                    <div
                      key={index}
                      className="rounded-lg border p-5"
                    >

                      <h3 className="truncate font-semibold text-lg" title={file.file}>

                        {file.file}

                      </h3>

                      <p className="mt-2 text-muted-foreground">

                        {file.review.summary}

                      </p>

                      <div className="mt-5 space-y-3">

                        {file.review.comments.length === 0 ? (

                          <div className="flex items-center gap-2 rounded-md bg-muted p-3 text-muted-foreground">
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                            No issues found.
                          </div>

                        ) : (

                          file.review.comments.map((comment, idx) => (

                            <div
                              key={idx}
                              className="rounded-md bg-muted p-3"
                            >

                              <div className="flex justify-between">

                                <span>

                                  Line {comment.line}

                                </span>

                                <Badge variant={getSeverityVariant(comment.severity)}>

                                  {comment.severity}

                                </Badge>

                              </div>

                              <p className="mt-2">

                                {comment.comment}

                              </p>

                            </div>

                          ))

                        )}

                      </div>

                    </div>

                  ))}

                </div>

              </div>

            </>

          )}

        </div>

        <DrawerFooter>

          <DrawerClose asChild>

            <Button>

              Close

            </Button>

          </DrawerClose>

        </DrawerFooter>

      </DrawerContent>

    </Drawer>

  )

}