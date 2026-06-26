// Lightweight Charts — gráfico de ticks com indicadores
import { useEffect, useRef } from 'react'
import { createChart, type IChartApi, type ISeriesApi, ColorType, LineStyle } from 'lightweight-charts'
import type { Tick } from '../types'

interface TradeChartProps {
  ticks: Tick[]
  symbol?: string
  showSMA?: boolean
}

export function TradeChart({ ticks, symbol = 'R_100', showSMA = true }: TradeChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeries = useRef<ISeriesApi<'Area'> | null>(null)
  const smaSeries = useRef<ISeriesApi<'Line'> | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#12121a' },
        textColor: '#6b6b80',
      },
      grid: {
        vertLines: { color: '#1e1e2a' },
        horzLines: { color: '#1e1e2a' },
      },
      width: containerRef.current.clientWidth,
      height: 400,
      crosshair: {
        vertLine: { labelBackgroundColor: '#f86525' },
        horzLine: { labelBackgroundColor: '#f86525' },
      },
      timeScale: {
        borderColor: '#2a2a3a',
        timeVisible: true,
      },
      rightPriceScale: {
        borderColor: '#2a2a3a',
      },
    })

    const areaSeries = chart.addAreaSeries({
      lineColor: '#f86525',
      topColor: 'rgba(248, 101, 37, 0.3)',
      bottomColor: 'rgba(248, 101, 37, 0.01)',
      lineWidth: 2,
    })

    const lineSeries = chart.addLineSeries({
      color: '#ffd64f',
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      lastValueVisible: false,
      priceFormat: { type: 'price', precision: 2 },
    })

    chartRef.current = chart
    candlestickSeries.current = areaSeries
    smaSeries.current = lineSeries

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  // Update data
  useEffect(() => {
    if (!candlestickSeries.current || ticks.length === 0) return

    const chartData = ticks.map((t) => ({
      time: t.epoch as any,
      value: t.quote,
    }))
    candlestickSeries.current.setData(chartData)

    // SMA calculation (simple for display)
    if (showSMA && ticks.length >= 20) {
      const smaData = ticks.map((t, i) => {
        if (i < 19) return null
        const slice = ticks.slice(i - 19, i + 1)
        const avg = slice.reduce((a, b) => a + b.quote, 0) / slice.length
        return { time: t.epoch as any, value: avg }
      }).filter(Boolean) as any[]
      smaSeries.current?.setData(smaData)
    }
  }, [ticks, showSMA])

  // Fit content when ticks change
  useEffect(() => {
    if (chartRef.current && ticks.length > 0) {
      chartRef.current.timeScale().fitContent()
    }
  }, [ticks.length])

  return (
    <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[#1e1e2a]">
        <span className="text-sm font-medium text-white">{symbol}</span>
        <span className="text-xs text-[#6b6b80]">
          {ticks.length} ticks · SMA {showSMA ? '✓' : '✗'}
        </span>
      </div>
      <div ref={containerRef} className="w-full" />
    </div>
  )
}
