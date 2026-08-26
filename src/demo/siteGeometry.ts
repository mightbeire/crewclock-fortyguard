import type { Workface } from './scenario'

export type SiteGeometry = {
  aoi: { type: 'FeatureCollection'; features: Array<{ type: 'Feature'; properties: Record<string, string>; geometry: { type: 'Polygon'; coordinates: number[][][] } }> }
  workfaces: Workface[]
  anchor: { latitude: number; longitude: number }
  dimensions_m: { width: number; height: number }
  precision: 'APPROXIMATE_OPERATOR_ANCHOR_DERIVED'
}

const us = (latitude: number, longitude: number) => Number.isFinite(latitude) && Number.isFinite(longitude) && latitude >= 24 && latitude <= 50 && longitude >= -125 && longitude <= -66

export const createSiteGeometry = (latitude: number, longitude: number, width: number, height: number): SiteGeometry => {
  if (!us(latitude, longitude)) throw new Error('Enter a latitude/longitude inside the supported United States.')
  if (!Number.isFinite(width) || !Number.isFinite(height) || width < 20 || height < 20 || width > 1000 || height > 1000) throw new Error('Site dimensions must be between 20 m and 1,000 m.')
  const latDelta = height / 111320 / 2
  const lonDelta = width / (111320 * Math.max(0.2, Math.cos(latitude * Math.PI / 180))) / 2
  const west = longitude - lonDelta; const east = longitude + lonDelta; const south = latitude - latDelta; const north = latitude + latDelta; const midLon = longitude; const midLat = latitude
  const face = (id: string, label: string, polygon: Array<[number, number]>): Workface => ({ id, label, polygon, geometry_precision: 'APPROXIMATE_OPERATOR_ANCHOR_DERIVED', source: 'OPERATOR_ANCHOR_AND_APPROXIMATE_SITE_DIMENSIONS' })
  const workfaces = [
    face('site-northwest', 'Northwest workface', [[west, midLat], [midLon, midLat], [midLon, north], [west, north]]),
    face('site-northeast', 'Northeast workface', [[midLon, midLat], [east, midLat], [east, north], [midLon, north]]),
    face('site-southwest', 'Southwest workface', [[west, south], [midLon, south], [midLon, midLat], [west, midLat]]),
    face('site-southeast', 'Southeast workface', [[midLon, south], [east, south], [east, midLat], [midLon, midLat]]),
  ]
  const ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
  return { aoi: { type: 'FeatureCollection', features: [{ type: 'Feature', properties: { label: 'Operator-entered site AOI', geometry_precision: 'APPROXIMATE_OPERATOR_ANCHOR_DERIVED' }, geometry: { type: 'Polygon', coordinates: [ring] } }] }, workfaces, anchor: { latitude, longitude }, dimensions_m: { width, height }, precision: 'APPROXIMATE_OPERATOR_ANCHOR_DERIVED' }
}

export const NEW_SITE_WORKFACE_OPTIONS = ['site-northwest', 'site-northeast', 'site-southwest', 'site-southeast']
