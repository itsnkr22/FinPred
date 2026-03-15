<template>
  <div class="app-layout">
    <nav class="sidebar">
      <div class="sidebar-header">
        <h1 class="logo">MiroFish</h1>
        <span class="logo-sub">FinPredict</span>
      </div>
      <ul class="nav-links">
        <li>
          <NuxtLink to="/" class="nav-link">
            <span class="nav-icon">&#9632;</span> Dashboard
          </NuxtLink>
        </li>
        <li>
          <NuxtLink to="/scenarios" class="nav-link">
            <span class="nav-icon">&#9654;</span> Scenarios
          </NuxtLink>
        </li>
        <li>
          <NuxtLink to="/commodities" class="nav-link">
            <span class="nav-icon">&#9679;</span> Commodities
          </NuxtLink>
        </li>
        <li>
          <NuxtLink to="/scenarios/new" class="nav-link">
            <span class="nav-icon">+</span> New Simulation
          </NuxtLink>
        </li>
      </ul>
      <div class="sidebar-footer">
        <span class="version">v1.0.0 MVP</span>
      </div>
    </nav>
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
}

.sidebar-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid var(--color-border);
}

.logo {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
}

.logo-sub {
  font-size: 12px;
  color: var(--color-text-secondary);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.nav-links {
  list-style: none;
  padding: 16px 0;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-text);
  background: rgba(59, 130, 246, 0.1);
  border-right: 2px solid var(--color-primary);
}

.nav-icon {
  font-size: 12px;
  width: 20px;
  text-align: center;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
}

.version {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.main-content {
  flex: 1;
  margin-left: 240px;
  padding: 32px;
}
</style>
