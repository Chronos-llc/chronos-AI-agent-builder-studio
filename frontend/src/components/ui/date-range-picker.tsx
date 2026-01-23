import * as React from "react"
import { format } from "date-fns"
import { Calendar as CalendarIcon } from "lucide-react"
import { cn } from "../../lib/utils"

interface DateRangePickerProps {
  date?: { from: Date; to: Date }
  onDateChange: (date?: { from: Date; to: Date }) => void
  className?: string
}

export function DatePickerWithRange({ date, onDateChange, className }: DateRangePickerProps) {
    const [isOpen, setIsOpen] = React.useState(false)
    const [from, setFrom] = React.useState<Date | undefined>(date?.from)
    const [to, setTo] = React.useState<Date | undefined>(date?.to)

    React.useEffect(() => {
        setFrom(date?.from)
        setTo(date?.to)
    }, [date])

    const handleConfirm = () => {
        if (from && to) {
            onDateChange({ from, to })
        } else if (from) {
            onDateChange({ from, to: from })
        }
        setIsOpen(false)
    }

    const handleClear = () => {
        setFrom(undefined)
        setTo(undefined)
        onDateChange(undefined)
        setIsOpen(false)
    }

    return (
        <div className={cn("relative", className)}>
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className={cn(
                    "w-full h-10 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-left text-sm text-white flex items-center gap-2",
                    "hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                )}
            >
                <CalendarIcon className="w-4 h-4 text-gray-400" />
                {date?.from && date?.to ? (
                    <span>
                        {format(date.from, "MMM d, yyyy")} - {format(date.to, "MMM d, yyyy")}
                    </span>
                ) : date?.from ? (
                    <span>
                        {format(date.from, "MMM d, yyyy")} - Select end date
                    </span>
                ) : (
                    <span className="text-gray-400">Select date range</span>
                )}
            </button>

            {isOpen && (
                <div className="absolute z-50 top-full mt-1 p-3 bg-gray-800 border border-gray-700 rounded-md shadow-lg">
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">From</label>
                            <input
                                type="date"
                                value={from ? format(from, "yyyy-MM-dd") : ""}
                                onChange={(e) => setFrom(e.target.value ? new Date(e.target.value) : undefined)}
                                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-sm text-white"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">To</label>
                            <input
                                type="date"
                                value={to ? format(to, "yyyy-MM-dd") : ""}
                                min={from ? format(from, "yyyy-MM-dd") : undefined}
                                onChange={(e) => setTo(e.target.value ? new Date(e.target.value) : undefined)}
                                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-sm text-white"
                            />
                        </div>
                        <div className="flex gap-2 pt-2">
                            <button
                                type="button"
                                onClick={handleClear}
                                className="flex-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-white"
                            >
                                Clear
                            </button>
                            <button
                                type="button"
                                onClick={handleConfirm}
                                className="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-sm text-white"
                            >
                                Apply
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}