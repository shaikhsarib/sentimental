export const DEFAULT_MAX_VISIBLE_NODES = 10000

const getId = (value) => {
  if (!value) return ''
  if (typeof value === 'string') return value
  return value.id || value.source || value.target || ''
}

const normalizeKey = (key) => String(key || 'UNKNOWN').replace(/\s+/g, '_')

const unpackKeyData = (keyData) => {
  if (typeof keyData === 'string') {
    return { key: normalizeKey(keyData), label: keyData, color: undefined }
  }
  if (!keyData || typeof keyData !== 'object') {
    return { key: 'UNKNOWN', label: 'Unknown', color: undefined }
  }
  return {
    key: normalizeKey(keyData.key || keyData.label || 'UNKNOWN'),
    label: keyData.label || keyData.key || 'Unknown',
    color: keyData.color
  }
}

export const buildClusterGraph = (nodes, links, keyFn) => {
  const clusters = new Map()
  const nodeToCluster = new Map()

  nodes.forEach((node) => {
    const keyData = unpackKeyData(keyFn(node))
    const clusterId = `cluster:${keyData.key}`

    if (!clusters.has(clusterId)) {
      clusters.set(clusterId, {
        id: clusterId,
        label: keyData.label,
        color: keyData.color,
        members: [],
        memberCount: 0
      })
    }

    const cluster = clusters.get(clusterId)
    cluster.members.push(node.id)
    cluster.memberCount += 1
    nodeToCluster.set(node.id, clusterId)
  })

  const clusterNodes = Array.from(clusters.values()).map((cluster) => {
    const size = Math.min(16, Math.max(4, Math.log(cluster.memberCount + 1) * 4))
    return {
      id: cluster.id,
      label: cluster.label,
      val: size,
      isCluster: true,
      memberCount: cluster.memberCount,
      color: cluster.color || '#94a3b8'
    }
  })

  const edgeMap = new Map()
  links.forEach((link) => {
    const sourceId = getId(link.source)
    const targetId = getId(link.target)
    if (!sourceId || !targetId) return

    const sourceCluster = nodeToCluster.get(sourceId)
    const targetCluster = nodeToCluster.get(targetId)
    if (!sourceCluster || !targetCluster || sourceCluster === targetCluster) return

    const [a, b] = sourceCluster < targetCluster ? [sourceCluster, targetCluster] : [targetCluster, sourceCluster]
    const key = `${a}__${b}`
    const weight = (link.weight || link.value || 1)

    if (!edgeMap.has(key)) {
      edgeMap.set(key, { source: a, target: b, value: weight })
    } else {
      edgeMap.get(key).value += weight
    }
  })

  return {
    graph: {
      nodes: clusterNodes,
      links: Array.from(edgeMap.values())
    },
    clusters: Object.fromEntries(clusters)
  }
}

export const buildSubgraph = (nodes, links, memberIds) => {
  const memberSet = new Set(memberIds)
  const subNodes = nodes.filter((node) => memberSet.has(node.id))
  const subLinks = links.filter((link) => {
    const sourceId = getId(link.source)
    const targetId = getId(link.target)
    return memberSet.has(sourceId) && memberSet.has(targetId)
  })

  return { nodes: subNodes, links: subLinks }
}
