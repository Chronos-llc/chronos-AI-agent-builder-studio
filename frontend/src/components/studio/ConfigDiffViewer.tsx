/**
 * ConfigDiffViewer Component
 * Side-by-side diff comparison with navigation and filtering
 */

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { DiffEntry, ChangeType } from '../../types/configManagement';

interface ConfigDiffViewerProps {
    configA: Record<string, unknown>;
    configB: Record<string, unknown>;
    differences?: DiffEntry[];
    onCompare?: (configA: Record<string, unknown>, configB: Record<string, unknown>) => void;
    title?: string;
}

const ConfigDiffViewer: React.FC<ConfigDiffViewerProps> = ({
    configA,
    configB,
    differences: initialDifferences = [],
    onCompare,
    title = 'Configuration Diff Viewer',
}) => {
    const [filter, setFilter] = useState<ChangeType | 'ALL'>('ALL');
    const [searchTerm, setSearchTerm] = useState('');
    const [jsonInputA, setJsonInputA] = useState(JSON.stringify(configA, null, 2));
    const [jsonInputB, setJsonInputB] = useState(JSON.stringify(configB, null, 2));
    const [parsedConfigA, setParsedConfigA] = useState<Record<string, unknown>>(configA);
    const [parsedConfigB, setParsedConfigB] = useState<Record<string, unknown>>(configB);
    const [parseError, setParseError] = useState<string | null>(null);

    const differences = useMemo(() => {
        if (initialDifferences.length > 0) return initialDifferences;

        // Calculate diffs if not provided
        const diffs: DiffEntry[] = [];
        compareObjects('', configA, configB, diffs);
        return diffs;
    }, [initialDifferences, configA, configB]);

    const filteredDifferences = useMemo(() => {
        return differences.filter((diff) => {
            // Apply type filter
            if (filter !== 'ALL' && diff.change_type !== filter) {
                return false;
            }
            // Apply search filter
            if (searchTerm && !diff.path.toLowerCase().includes(searchTerm.toLowerCase())) {
                return false;
            }
            return true;
        });
    }, [differences, filter, searchTerm]);

    const stats = useMemo(() => {
        const added = differences.filter(d => d.change_type === 'ADDED').length;
        const removed = differences.filter(d => d.change_type === 'REMOVED').length;
        const modified = differences.filter(d => d.change_type === 'MODIFIED').length;
        return { added, removed, modified, total: differences.length };
    }, [differences]);

    function compareObjects(
        path: string,
        objA: Record<string, unknown>,
        objB: Record<string, unknown>,
        diffs: DiffEntry[]
    ) {
        const allKeys = new Set([...Object.keys(objA || {}), ...Object.keys(objB || {})]);

        allKeys.forEach((key) => {
            const newPath = path ? `${path}.${key}` : key;
            const valA = objA?.[key];
            const valB = objB?.[key];

            if (valA === undefined && valB !== undefined) {
                diffs.push({
                    path: newPath,
                    old_value: undefined,
                    new_value: valB,
                    change_type: 'ADDED',
                });
            } else if (valA !== undefined && valB === undefined) {
                diffs.push({
                    path: newPath,
                    old_value: valA,
                    new_value: undefined,
                    change_type: 'REMOVED',
                });
            } else if (JSON.stringify(valA) !== JSON.stringify(valB)) {
                if (
                    typeof valA === 'object' &&
                    valA !== null &&
                    typeof valB === 'object' &&
                    valB !== null
                ) {
                    compareObjects(newPath, valA as Record<string, unknown>, valB as Record<string, unknown>, diffs);
                } else {
                    diffs.push({
                        path: newPath,
                        old_value: valA,
                        new_value: valB,
                        change_type: 'MODIFIED',
                    });
                }
            }
        });
    }

    const handleInputChangeA = (value: string) => {
        setJsonInputA(value);
        try {
            setParsedConfigA(JSON.parse(value));
            setParseError(null);
        } catch (e) {
            setParseError('Invalid JSON in configuration A');
        }
    };

    const handleInputChangeB = (value: string) => {
        setJsonInputB(value);
        try {
            setParsedConfigB(JSON.parse(value));
            setParseError(null);
        } catch (e) {
            setParseError('Invalid JSON in configuration B');
        }
    };

    const handleCompareClick = () => {
        if (parseError) {
            alert('Please fix JSON errors before comparing');
            return;
        }
        onCompare?.(parsedConfigA, parsedConfigB);
    };

    const exportDiffReport = () => {
        const report = {
            generated_at: new Date().toISOString(),
            summary: stats,
            differences: filteredDifferences,
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'diff-report.json';
        a.click();
        URL.revokeObjectURL(url);
    };

    const getChangeBadge = (type: ChangeType) => {
        switch (type) {
            case 'ADDED':
                return <Badge className="bg-green-500">ADDED</Badge>;
            case 'REMOVED':
                return <Badge variant="destructive">REMOVED</Badge>;
            case 'MODIFIED':
                return <Badge className="bg-yellow-500">MODIFIED</Badge>;
        }
    };

    const getValueDisplay = (value: unknown): string => {
        if (value === undefined) return '<undefined>';
        if (value === null) return '<null>';
        if (typeof value === 'object') return JSON.stringify(value, null, 2);
        return String(value);
    };

    return (
        <div className="config-diff-viewer p-4 space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">{title}</h2>
                <Button onClick={exportDiffReport} variant="outline">
                    Export Report
                </Button>
            </div>

            {/* Stats */}
            <div className="flex gap-4">
                <Card className="flex-1">
                    <CardContent className="pt-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-500">Total Changes</span>
                            <Badge variant="outline">{stats.total}</Badge>
                        </div>
                    </CardContent>
                </Card>
                <Card className="flex-1">
                    <CardContent className="pt-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-500">Added</span>
                            <Badge className="bg-green-500">{stats.added}</Badge>
                        </div>
                    </CardContent>
                </Card>
                <Card className="flex-1">
                    <CardContent className="pt-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-500">Removed</span>
                            <Badge variant="destructive">{stats.removed}</Badge>
                        </div>
                    </CardContent>
                </Card>
                <Card className="flex-1">
                    <CardContent className="pt-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-500">Modified</span>
                            <Badge className="bg-yellow-500">{stats.modified}</Badge>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Input Section */}
            {onCompare && (
                <Card>
                    <CardHeader>
                        <CardTitle>Compare Configurations</CardTitle>
                        <CardDescription>
                            Paste two JSON configurations to compare them
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium">Configuration A (Original)</label>
                                <textarea
                                    className={`w-full h-48 p-3 border rounded-md font-mono text-sm ${parseError ? 'border-red-500' : 'bg-gray-50'
                                        }`}
                                    value={jsonInputA}
                                    onChange={(e) => handleInputChangeA(e.target.value)}
                                    placeholder="{}"
                                />
                            </div>
                            <div>
                                <label className="text-sm font-medium">Configuration B (New)</label>
                                <textarea
                                    className={`w-full h-48 p-3 border rounded-md font-mono text-sm ${parseError ? 'border-red-500' : 'bg-gray-50'
                                        }`}
                                    value={jsonInputB}
                                    onChange={(e) => handleInputChangeB(e.target.value)}
                                    placeholder="{}"
                                />
                            </div>
                        </div>
                        <Button className="mt-4" onClick={handleCompareClick} disabled={!!parseError}>
                            Compare Configurations
                        </Button>
                    </CardContent>
                </Card>
            )}

            {/* Side-by-side view */}
            <Card>
                <CardHeader>
                    <CardTitle>Side-by-Side Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="text-sm font-medium mb-2">Configuration A</div>
                            <pre className="h-64 p-3 border rounded-md bg-red-50 text-sm overflow-auto">
                                {JSON.stringify(parsedConfigA, null, 2)}
                            </pre>
                        </div>
                        <div>
                            <div className="text-sm font-medium mb-2">Configuration B</div>
                            <pre className="h-64 p-3 border rounded-md bg-green-50 text-sm overflow-auto">
                                {JSON.stringify(parsedConfigB, null, 2)}
                            </pre>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Diff List */}
            <Card>
                <CardHeader>
                    <div className="flex justify-between items-center">
                        <CardTitle>Differences</CardTitle>
                        <div className="flex gap-2">
                            <Input
                                placeholder="Search paths..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-48"
                            />
                            <Select value={filter} onValueChange={(val) => setFilter(val as ChangeType | 'ALL')}>
                                <SelectTrigger className="w-40">
                                    <SelectValue placeholder="Filter" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="ALL">All Changes</SelectItem>
                                    <SelectItem value="ADDED">Added</SelectItem>
                                    <SelectItem value="REMOVED">Removed</SelectItem>
                                    <SelectItem value="MODIFIED">Modified</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <ScrollArea className="h-96">
                        {filteredDifferences.length === 0 ? (
                            <div className="text-center py-8 text-gray-500">
                                {differences.length === 0
                                    ? 'No differences found - configurations are identical'
                                    : 'No differences match your filters'}
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {filteredDifferences.map((diff, idx) => (
                                    <div
                                        key={idx}
                                        className={`p-3 border rounded-lg ${diff.change_type === 'ADDED'
                                                ? 'bg-green-50 border-green-200'
                                                : diff.change_type === 'REMOVED'
                                                    ? 'bg-red-50 border-red-200'
                                                    : 'bg-yellow-50 border-yellow-200'
                                            }`}
                                    >
                                        <div className="flex items-center gap-2 mb-2">
                                            {getChangeBadge(diff.change_type)}
                                            <code className="text-sm font-mono">{diff.path}</code>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            {diff.change_type !== 'ADDED' && (
                                                <div>
                                                    <span className="text-red-600 font-medium">Old:</span>
                                                    <pre className="mt-1 p-2 bg-red-100 rounded text-xs overflow-auto max-h-32">
                                                        {getValueDisplay(diff.old_value)}
                                                    </pre>
                                                </div>
                                            )}
                                            {diff.change_type !== 'REMOVED' && (
                                                <div>
                                                    <span className="text-green-600 font-medium">New:</span>
                                                    <pre className="mt-1 p-2 bg-green-100 rounded text-xs overflow-auto max-h-32">
                                                        {getValueDisplay(diff.new_value)}
                                                    </pre>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </ScrollArea>
                </CardContent>
            </Card>
        </div>
    );
};

export default ConfigDiffViewer;
