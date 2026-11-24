<template>
  <div class="admin-dash">
    <div class="container">
      <div class="dash-header fade-up">
        <h1>{{ t('admin.title') }}</h1>
        <nav class="nav-links">
          <router-link to="/admin" class="nav-active">{{ t('admin.overview') }}</router-link>
          <router-link to="/admin/inquiries" class="nav-inq">
            {{ t('admin.inquiries') }}
            <span v-if="unreadInquiries > 0" class="nav-badge">{{ unreadInquiries }}</span>
          </router-link>
        </nav>
      </div>

      <div class="stats-grid fade-up fade-up-d1">
        <div class="stat-card"><span class="stat-num">{{ stats.total_factories }}</span><span>{{ t('admin.factories') }}</span></div>
        <div class="stat-card"><span class="stat-num warn">{{ stats.pending_factories }}</span><span>{{ t('admin.pendingF') }}</span></div>
        <div class="stat-card"><span class="stat-num">{{ stats.total_products }}</span><span>{{ t('admin.totalProducts') }}</span></div>
        <div class="stat-card"><span class="stat-num ok">{{ stats.active_products }}</span><span>{{ t('admin.sActive') }}</span></div>
        <div class="stat-card"><span class="stat-num blue">{{ stats.pending_products }}</span><span>{{ t('admin.sPending') }}</span></div>
        <div class="stat-card"><span class="stat-num danger">{{ stats.rejected_products }}</span><span>{{ t('admin.sRejected') }}</span></div>
      </div>

      <el-tabs v-model="activeTab" class="fade-up fade-up-d2">
        <el-tab-pane v-if="isB2B" :label="t('admin.factoryApproval')" name="factories">
          <el-table :data="factories" style="width:100%">
            <el-table-column prop="company_name" :label="t('admin.company')" min-width="130" />
            <el-table-column prop="contact_person" :label="t('admin.contact')" width="90" />
            <el-table-column prop="email" :label="t('admin.email')" width="150" show-overflow-tooltip />
            <el-table-column prop="phone" :label="t('admin.phone')" width="110" />
            <el-table-column :label="t('admin.products')" width="60" align="center">
              <template #default="{ row }">{{ row.product_count || 0 }}</template>
            </el-table-column>
            <el-table-column prop="status" :label="t('factory.status')" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'pending' ? 'warning' : row.status === 'disabled' ? 'info' : 'danger'" size="small">{{ factoryStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('admin.joinDate')" width="110">
              <template #default="{ row }"><span style="white-space:nowrap">{{ formatDate(row.created_at) }}</span></template>
            </el-table-column>
            <el-table-column :label="t('factory.actions')" width="260">
              <template #default="{ row }">
                <el-button size="small" @click="openFactoryDetail(row)">{{ t('admin.view') }}</el-button>
                <template v-if="row.status === 'pending'">
                  <el-button size="small" type="success" @click="approveFactory(row.id)">{{ t('admin.approve') }}</el-button>
                  <el-button size="small" type="danger" @click="openRejectFactoryDialog(row)">{{ t('admin.reject') }}</el-button>
                </template>
                <template v-if="row.status === 'approved'">
                  <el-button size="small" type="warning" @click="disableFactory(row.id)">{{ isZh ? '禁用' : 'Disable' }}</el-button>
                </template>
                <template v-if="row.status === 'disabled'">
                  <el-button size="small" type="success" @click="enableFactory(row.id)">{{ isZh ? '启用' : 'Enable' }}</el-button>
                </template>
                <el-popconfirm :title="isZh ? '确认删除该工厂及其所有产品？' : 'Delete this factory and all its products?'" @confirm="deleteFactory(row.id)">
                  <template #reference>
                    <el-button v-if="row.status !== 'pending'" size="small" type="danger" plain>{{ t('admin.delete') }}</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane v-if="isB2B" :label="t('admin.productApproval')" name="products">
          <div class="filter-bar">
            <el-radio-group v-model="productFilter" @change="loadProducts" size="small">
              <el-radio-button value="all">{{ t('admin.all') }}</el-radio-button>
              <el-radio-button value="pending">{{ t('admin.sPending') }}</el-radio-button>
              <el-radio-button value="active">{{ t('admin.sActive') }}</el-radio-button>
              <el-radio-button value="rejected">{{ t('admin.sRejected') }}</el-radio-button>
            </el-radio-group>
          </div>
          <el-table :data="products" style="width:100%">
            <el-table-column :label="t('admin.product')" min-width="200">
              <template #default="{ row }">
                <div class="prod-cell">
                  <img v-if="row.images && row.images.length" :src="row.images[0]" class="prod-thumb" />
                  <span>{{ row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="factory_name" :label="t('admin.factory')" width="130" />
            <el-table-column label="MOQ" width="70" class-name="no-wrap-col">
              <template #default="{ row }">{{ row.moq }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.basePrice')" width="100" class-name="no-wrap-col">
              <template #default="{ row }"><span class="price-admin">${{ row.base_price }}</span></template>
            </el-table-column>
            <el-table-column prop="status" :label="t('factory.status')" width="95">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="标记" width="180">
              <template #default="{ row }">
                <el-tag v-if="row.is_featured" type="warning" size="small" style="margin-right:4px">★</el-tag>
                <el-tag v-if="row.is_new" type="success" size="small" style="margin-right:4px">NEW</el-tag>
                <el-tag v-if="row.is_clearance" type="danger" size="small" style="margin-right:4px">清仓</el-tag>
                <el-tag v-if="row.is_banner" type="primary" size="small">Banner</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('factory.actions')" min-width="220">
              <template #default="{ row }">
                <el-button size="small" @click="openViewDialog(row)">{{ t('admin.view') }}</el-button>
                <el-button size="small" @click="editProduct(row)">{{ t('factory.edit') }}</el-button>
                <el-dropdown trigger="click" @command="cmd => handleProductAction(cmd, row)" style="margin-left:8px">
                  <el-button size="small">{{ isZh ? '更多' : 'More' }} ▾</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-if="row.status === 'pending'" command="approve">{{ t('admin.approve') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'pending'" command="reject">{{ t('admin.reject') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="offline">{{ t('admin.takeOffline') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="feature">{{ row.is_featured ? t('admin.unfeature') : t('admin.feature') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="new">{{ row.is_new ? t('admin.unsetNew') : t('admin.setNew') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="banner">{{ row.is_banner ? (isZh ? '取消Banner' : 'Unbanner') : 'Banner' }}</el-dropdown-item>
                      <el-dropdown-item command="delete" divided style="color:#ef4444">{{ t('admin.delete') }}</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- B2C模式：商品管理 -->
        <el-tab-pane v-if="isB2C" :label="isZh ? '商品管理' : 'Product Management'" name="b2c-products">
          <div class="filter-bar">
            <el-button type="primary" size="small" @click="router.push('/admin/products/new')">+ {{ isZh ? '添加商品' : 'Add Product' }}</el-button>
          </div>
          <el-table :data="products" style="width:100%">
            <el-table-column :label="t('admin.product')" min-width="200">
              <template #default="{ row }">
                <div class="prod-cell">
                  <img v-if="row.images && row.images.length" :src="row.images[0]" class="prod-thumb" />
                  <span>{{ row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="MOQ" width="70" class-name="no-wrap-col">
              <template #default="{ row }">{{ row.moq }}</template>
            </el-table-column>
            <el-table-column :label="t('admin.basePrice')" width="100" class-name="no-wrap-col">
              <template #default="{ row }"><span class="price-admin">${{ row.base_price }}</span></template>
            </el-table-column>
            <el-table-column prop="status" :label="t('factory.status')" width="95">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="isZh ? '标记' : 'Tags'" width="180">
              <template #default="{ row }">
                <el-tag v-if="row.is_featured" type="warning" size="small" style="margin-right:4px">★</el-tag>
                <el-tag v-if="row.is_new" type="success" size="small" style="margin-right:4px">NEW</el-tag>
                <el-tag v-if="row.is_clearance" type="danger" size="small" style="margin-right:4px">{{ isZh ? '清仓' : 'Clearance' }}</el-tag>
                <el-tag v-if="row.is_banner" type="primary" size="small">Banner</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('factory.actions')" min-width="220">
              <template #default="{ row }">
                <el-button size="small" @click="openViewDialog(row)">{{ t('admin.view') }}</el-button>
                <el-button size="small" @click="editProduct(row)">{{ t('admin.edit') }}</el-button>
                <el-dropdown trigger="click" @command="cmd => handleProductAction(cmd, row)" style="margin-left:8px">
                  <el-button size="small">{{ isZh ? '更多' : 'More' }} ▾</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-if="row.status === 'pending'" command="approve">{{ t('admin.approve') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'pending'" command="reject">{{ t('admin.reject') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="offline">{{ t('admin.takeOffline') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="feature">{{ row.is_featured ? t('admin.unfeature') : t('admin.feature') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="new">{{ row.is_new ? t('admin.unsetNew') : t('admin.setNew') }}</el-dropdown-item>
                      <el-dropdown-item v-if="row.status === 'active'" command="banner">{{ row.is_banner ? (isZh ? '取消Banner' : 'Unbanner') : 'Banner' }}</el-dropdown-item>
                      <el-dropdown-item command="delete" divided style="color:#ef4444">{{ t('admin.delete') }}</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('admin.analytics')" name="analytics">
          <div class="analytics-container">
            <div class="chart-section">
              <h3>{{ t('admin.inquiriesTrend') }}</h3>
              <div v-if="analytics.inquiries_by_date && analytics.inquiries_by_date.length" class="bar-chart">
                <div v-for="item in analytics.inquiries_by_date" :key="item.date" class="bar-row">
                  <span class="bar-label">{{ item.date }}</span>
                  <div class="bar-track">
                    <div class="bar-fill primary" :style="{ width: barWidth(item.count, maxInqByDate) }"></div>
                  </div>
                  <span class="bar-value">{{ item.count }}</span>
                </div>
              </div>
              <div v-else class="empty-chart">暂无数据</div>
            </div>
            <div class="chart-section">
              <h3>{{ t('admin.inquiriesByStatus') }}</h3>
              <div v-if="analytics.inquiries_by_status && analytics.inquiries_by_status.length" class="bar-chart">
                <div v-for="item in analytics.inquiries_by_status" :key="item.status" class="bar-row">
                  <span class="bar-label">{{ statusLabelInq(item.status) }}</span>
                  <div class="bar-track">
                    <div class="bar-fill" :class="statusColor(item.status)" :style="{ width: barWidth(item.count, maxInqByStatus) }"></div>
                  </div>
                  <span class="bar-value">{{ item.count }}</span>
                </div>
              </div>
              <div v-else class="empty-chart">暂无数据</div>
            </div>
            <div class="chart-section">
              <h3>{{ t('admin.productsByCategory') }}</h3>
              <div v-if="analytics.products_by_category && analytics.products_by_category.length" class="bar-chart">
                <div v-for="item in analytics.products_by_category" :key="item.category" class="bar-row">
                  <span class="bar-label">{{ item.category }}</span>
                  <div class="bar-track">
                    <div class="bar-fill success" :style="{ width: barWidth(item.count, maxProdByCat) }"></div>
                  </div>
                  <span class="bar-value">{{ item.count }}</span>
                </div>
              </div>
              <div v-else class="empty-chart">暂无数据</div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="t('admin.customers')" name="customers">
          <el-table :data="customers" style="width:100%">
            <el-table-column prop="contact_name" :label="t('admin.contactName')" min-width="130" />
            <el-table-column prop="company_name" :label="t('admin.companyN')" min-width="160" />
            <el-table-column prop="email" :label="t('admin.emailE')" min-width="200" />
            <el-table-column prop="phone" :label="t('admin.phone')" min-width="140" />
            <el-table-column :label="isZh ? '来源' : 'Source'" min-width="100">
              <template #default="{ row }">
                <el-tag v-if="row.source" size="small" type="info">{{ row.source }}</el-tag>
                <span v-else style="color:var(--text-secondary);font-size:12px">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="inquiry_count" :label="t('admin.inquiries')" min-width="100" align="center" />
            <el-table-column :label="t('admin.joinDate')" width="110">
              <template #default="{ row }"><span style="white-space:nowrap">{{ formatDate(row.created_at) }}</span></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="isZh ? '分类管理' : 'Categories'" name="categories">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <span style="font-size:14px;color:#9ca3af">{{ catList.length }} {{ isZh ? '个主分类' : 'categories' }}</span>
            <el-button type="primary" size="small" @click="openCatDialog(null)">+ {{ isZh ? '添加分类' : 'Add Category' }}</el-button>
          </div>
          <div class="cat-tree-list">
            <div v-for="cat in catList" :key="cat.id" class="cat-tree-row">
              <div class="cat-row-main">
                <span class="cat-row-icon">{{ cat.icon || '📁' }}</span>
                <span class="cat-row-name">{{ cat.name }}</span>
                <span class="cat-row-en">{{ cat.name_en || '' }}</span>
                <span class="cat-row-order">#{{ cat.sort_order }}</span>
                <el-tag :type="cat.is_active ? 'success' : 'info'" size="small" style="cursor:pointer" @click="toggleCatActive(cat)">{{ cat.is_active ? (isZh ? '启用' : 'Active') : (isZh ? '停用' : 'Inactive') }}</el-tag>
                <span style="flex:1"></span>
                <el-button size="small" @click="openCatDialog(null, cat.id)">+ {{ isZh ? '子分类' : 'Sub' }}</el-button>
                <el-button size="small" @click="openCatDialog(cat)">{{ t('factory.edit') }}</el-button>
                <el-popconfirm :title="isZh ? '确认删除？子分类也会被删除' : 'Delete? Children will also be removed'" @confirm="deleteCat(cat.id)">
                  <template #reference><el-button size="small" type="danger">{{ t('admin.delete') }}</el-button></template>
                </el-popconfirm>
              </div>
              <div v-if="cat.children && cat.children.length" class="cat-children-list">
                <div v-for="child in cat.children" :key="child.id" class="cat-row-child">
                  <span class="cat-row-icon">{{ child.icon || '📄' }}</span>
                  <span class="cat-row-name">{{ child.name }}</span>
                  <span class="cat-row-en">{{ child.name_en || '' }}</span>
                  <span class="cat-row-order">#{{ child.sort_order }}</span>
                  <el-tag :type="child.is_active ? 'success' : 'info'" size="small" style="cursor:pointer" @click="toggleCatActive(child)">{{ child.is_active ? (isZh ? '启用' : 'Active') : (isZh ? '停用' : 'Inactive') }}</el-tag>
                  <span style="flex:1"></span>
                  <el-button size="small" @click="openCatDialog(child)">{{ t('factory.edit') }}</el-button>
                  <el-popconfirm :title="isZh ? '确认删除此子分类？' : 'Delete this subcategory?'" @confirm="deleteCat(child.id)">
                    <template #reference><el-button size="small" type="danger">{{ t('admin.delete') }}</el-button></template>
                  </el-popconfirm>
                </div>
              </div>
            </div>
            <div v-if="!catList.length" style="text-align:center;padding:40px 0;color:#9ca3af">{{ isZh ? '暂无分类' : 'No categories' }}</div>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="isZh ? '首页管理' : 'Homepage'" name="site">
          <div class="site-mgmt">
            <div class="site-section">
              <h3>{{ isZh ? '背景图片' : 'Background Image' }}</h3>
              <div class="site-img-upload">
                <el-input v-model="siteForm.hero_bg_image" :placeholder="isZh ? '图片URL或上传本地图片' : 'Image URL or upload'" />
                <el-button size="default" @click="$refs.heroBgInput.click()">{{ isZh ? '上传' : 'Upload' }}</el-button>
                <input ref="heroBgInput" type="file" accept="image/*" hidden @change="uploadHeroBg" />
              </div>
              <img v-if="siteForm.hero_bg_image" :src="siteForm.hero_bg_image" class="site-img-preview" />
            </div>

            <div v-for="sec in siteSections" :key="sec.key" class="site-section">
              <h3>{{ sec.label }}</h3>
              <!-- Eyebrow editor -->
              <div v-if="sec.eyebrowKey" class="site-eyebrow-row">
                <span class="site-label">{{ isZh ? '蓝色小标题' : 'Eyebrow' }}</span>
                <div class="site-eyebrow-langs">
                  <div v-for="lang in langs" :key="lang.code" class="site-eyebrow-item">
                    <span class="site-lang-tag">{{ lang.code }}</span>
                    <el-input v-model="siteForm['eyebrow_' + sec.eyebrowKey + '.' + lang.code]" size="small" />
                  </div>
                </div>
              </div>
              <el-tabs type="card" class="lang-tabs">
                <el-tab-pane v-for="lang in langs" :key="lang.code" :label="lang.name">
                  <div class="site-title-editor" :class="{ 'hero-layout': sec.key === 'hero' || sec.key === 'heroDesc' }">
                    <div v-for="(item, idx) in getSectionItems(sec.key, lang.code)" :key="idx" class="site-title-item">
                      <el-input v-model="item.text" size="default" :placeholder="isZh ? '输入文字' : 'Enter text'" />
                      <el-checkbox v-if="!sec.noGradient" v-model="item.gradient" :label="isZh ? '强调' : 'Emphasis'" class="gradient-check" />
                      <el-button type="danger" size="small" circle @click="removeSectionItem(sec.key, lang.code, idx)">✕</el-button>
                    </div>
                  </div>
                  <el-button size="small" style="margin-top:8px" @click="addSectionItem(sec.key, lang.code)">+ {{ isZh ? '添加文字' : 'Add text' }}</el-button>
                </el-tab-pane>
              </el-tabs>
            </div>

            <!-- Factory details -->
            <div class="site-section">
              <h3>{{ isZh ? '工厂直供 - 图片与描述' : 'Factory - Image & Description' }}</h3>
              <div class="site-img-upload">
                <el-input v-model="siteForm.factory_image" :placeholder="isZh ? '工厂图片URL' : 'Factory image URL'" />
                <el-button size="default" @click="$refs.factoryImgInput.click()">{{ isZh ? '上传' : 'Upload' }}</el-button>
                <input ref="factoryImgInput" type="file" accept="image/*" hidden @change="uploadFactoryImg" />
              </div>
              <img v-if="siteForm.factory_image" :src="siteForm.factory_image" class="site-img-preview" />
              <div style="margin-top:16px">
                <span class="site-label">{{ isZh ? '副标题' : 'Subtitle' }}</span>
                <div class="site-eyebrow-langs">
                  <div v-for="lang in langs" :key="lang.code" class="site-eyebrow-item">
                    <span class="site-lang-tag">{{ lang.code }}</span>
                    <el-input v-model="siteForm['factory_desc.' + lang.code]" size="small" />
                  </div>
                </div>
              </div>
              <div style="margin-top:16px">
                <span class="site-label">{{ isZh ? '4个数据卡片' : '4 Stat Cards' }}</span>
                <div v-for="(stat, idx) in factoryStats" :key="idx" class="site-stat-row">
                  <el-input v-model="stat.number" :placeholder="isZh ? '数字' : 'Number'" style="width:80px" size="small" />
                  <div v-for="lang in langs" :key="lang.code" class="site-stat-lang">
                    <span class="site-lang-tag">{{ lang.code }}</span>
                    <el-input v-model="stat['label_' + lang.code]" size="small" :placeholder="isZh ? '描述' : 'Label'" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Process steps -->
            <div class="site-section">
              <h3>{{ isZh ? '合作流程 - 步骤详情' : 'Process - Step Details' }}</h3>
              <div v-for="(step, idx) in processSteps" :key="idx" class="site-step-row">
                <div class="site-step-header">
                  <span class="site-step-num">{{ String(idx + 1).padStart(2, '0') }}</span>
                  <el-input v-model="step.icon" style="width:80px" size="small" :placeholder="isZh ? '图标/emoji' : 'Icon/emoji'" />
                  <el-button size="small" @click="$refs['stepImg' + idx][0].click()">{{ isZh ? '上传图片' : 'Upload' }}</el-button>
                  <input :ref="'stepImg' + idx" type="file" accept="image/*" hidden @change="e => uploadStepIcon(e, idx)" />
                  <img v-if="step.icon && step.icon.startsWith('/')" :src="step.icon" class="site-step-preview" />
                </div>
                <div class="site-eyebrow-langs">
                  <div v-for="lang in langs" :key="lang.code" class="site-eyebrow-item">
                    <span class="site-lang-tag">{{ lang.code }}</span>
                    <el-input v-model="step['title_' + lang.code]" size="small" :placeholder="isZh ? '标题' : 'Title'" />
                  </div>
                </div>
                <div class="site-eyebrow-langs" style="margin-top:6px">
                  <div v-for="lang in langs" :key="lang.code" class="site-eyebrow-item">
                    <span class="site-lang-tag">{{ lang.code }}</span>
                    <el-input v-model="step['desc_' + lang.code]" size="small" :placeholder="isZh ? '描述' : 'Desc'" />
                  </div>
                </div>
              </div>
            </div>

            <div style="text-align:right;margin-top:24px">
              <el-button type="primary" @click="saveSiteSettings" :loading="siteSaving">{{ isZh ? '保存设置' : 'Save Settings' }}</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- Category dialog -->
      <el-dialog v-model="showCatDialog" :title="catForm.id ? (isZh ? '编辑分类' : 'Edit Category') : (isZh ? '添加分类' : 'Add Category')" width="480px">
        <div style="display:flex;flex-direction:column;gap:14px">
          <div>
            <label class="cat-label">{{ isZh ? '中文名称' : 'Name (CN)' }} *</label>
            <el-input v-model="catForm.name" :placeholder="isZh ? '分类名称' : 'Category name'" />
          </div>
          <div>
            <label class="cat-label">{{ isZh ? '英文名称' : 'Name (EN)' }}</label>
            <el-input v-model="catForm.name_en" placeholder="English name" />
          </div>
          <div>
            <label class="cat-label">{{ isZh ? '上级分类' : 'Parent Category' }}</label>
            <el-select v-model="catForm.parent_id" :placeholder="isZh ? '无（顶级分类）' : 'None (top-level)'" clearable style="width:100%">
              <el-option v-for="c in catParentOptions" :key="c.id" :label="c.name + (c.name_en ? ' / ' + c.name_en : '')" :value="c.id" />
            </el-select>
          </div>
          <div style="display:flex;gap:14px">
            <div style="flex:1">
              <label class="cat-label">{{ isZh ? '图标' : 'Icon' }}</label>
              <el-input v-model="catForm.icon" placeholder="📦" />
            </div>
            <div style="flex:1">
              <label class="cat-label">{{ isZh ? '排序' : 'Sort Order' }}</label>
              <el-input-number v-model="catForm.sort_order" :min="0" style="width:100%" />
            </div>
          </div>
          <div v-if="catForm.id">
            <el-checkbox v-model="catForm.is_active">{{ isZh ? '启用' : 'Active' }}</el-checkbox>
          </div>
        </div>
        <template #footer>
          <el-button @click="showCatDialog = false">{{ t('factory.cancel') }}</el-button>
          <el-button type="primary" @click="saveCat" :disabled="!catForm.name.trim()">{{ isZh ? '保存' : 'Save' }}</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="showRejectDialog" :title="t('admin.rejectTitle')" width="480px">
        <p style="margin-bottom:12px;color:var(--text-secondary)">{{ rejectTarget?.title }}</p>
        <el-input v-model="rejectReason" type="textarea" :rows="3" :placeholder="t('admin.rejectPlaceholder')" />
        <template #footer>
          <el-button @click="showRejectDialog = false">{{ t('factory.cancel') }}</el-button>
          <el-button type="danger" @click="confirmReject" :disabled="!rejectReason.trim()">{{ t('admin.confirmReject') }}</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="showRejectFactoryDialog" :title="isZh ? '拒绝工厂' : 'Reject Factory'" width="480px">
        <p style="margin-bottom:12px;color:var(--text-secondary)">{{ rejectFactoryTarget?.company_name }}</p>
        <el-input v-model="rejectFactoryReason" type="textarea" :rows="3" :placeholder="isZh ? '请填写拒绝理由，工厂登录时将看到此信息' : 'Rejection reason (visible to factory on login)'" />
        <template #footer>
          <el-button @click="showRejectFactoryDialog = false">{{ t('admin.cancel') }}</el-button>
          <el-button type="danger" @click="confirmRejectFactory" :disabled="!rejectFactoryReason.trim()">{{ t('admin.reject') }}</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="showOfflineDialog" :title="t('admin.offlineTitle')" width="480px">
        <p style="margin-bottom:12px;color:var(--text-secondary)">{{ offlineTarget?.title }}</p>
        <el-input v-model="offlineReason" type="textarea" :rows="3" :placeholder="t('admin.offlineReason')" />
        <template #footer>
          <el-button @click="showOfflineDialog = false">{{ t('factory.cancel') }}</el-button>
          <el-button type="warning" @click="confirmOffline" :disabled="!offlineReason.trim()">{{ t('admin.confirmOffline') }}</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="showFactoryDetail" :title="factoryDetail?.company_name" width="600px">
        <div v-if="factoryDetail" class="factory-detail">
          <div class="detail-row"><strong>{{ t('admin.company') }}:</strong> {{ factoryDetail.company_name }}</div>
          <div class="detail-row"><strong>{{ t('admin.contact') }}:</strong> {{ factoryDetail.contact_person }}</div>
          <div class="detail-row"><strong>{{ t('admin.email') }}:</strong> {{ factoryDetail.email }}</div>
          <div class="detail-row"><strong>{{ t('admin.phone') }}:</strong> {{ factoryDetail.phone }}</div>
          <div class="detail-row"><strong>{{ t('admin.address') }}:</strong> {{ factoryDetail.address }}</div>
          <div class="detail-row"><strong>{{ t('factory.status') }}:</strong>
            <el-tag :type="factoryDetail.status === 'approved' ? 'success' : factoryDetail.status === 'pending' ? 'warning' : factoryDetail.status === 'disabled' ? 'info' : 'danger'" size="small">{{ factoryStatusLabel(factoryDetail.status) }}</el-tag>
          </div>
          <div class="detail-row"><strong>{{ t('admin.products') }}:</strong> {{ factoryDetail.product_count || 0 }} ({{ t('admin.sActive') }}: {{ factoryDetail.active_product_count || 0 }})</div>
          <div class="detail-row"><strong>{{ t('admin.inquiries') }}:</strong> {{ factoryDetail.inquiry_count || 0 }}</div>
          <div class="detail-row"><strong>{{ t('factory.totalViews') }}:</strong> {{ factoryDetail.total_views || 0 }}</div>
          <div class="detail-row" v-if="factoryDetail.description"><strong>{{ t('auth.desc') }}:</strong> {{ factoryDetail.description }}</div>
          <div class="detail-row" v-if="factoryDetail.certification_files && factoryDetail.certification_files.length">
            <strong>{{ isZh ? '认证资料' : 'Certifications' }}:</strong>
            <div class="cert-list">
              <a v-for="(f, i) in factoryDetail.certification_files" :key="i" :href="f" target="_blank" class="cert-link">{{ f.split('/').pop() }}</a>
            </div>
          </div>
        </div>
      </el-dialog>

      <el-dialog v-model="showViewDialog" :title="viewProduct?.title" width="700px">
        <div v-if="viewProduct" class="view-detail">
          <div class="view-images" v-if="viewProduct.images && viewProduct.images.length">
            <img v-for="(img, i) in viewProduct.images" :key="i" :src="img" class="view-img" />
          </div>
          <div v-if="viewProduct.poster_images && viewProduct.poster_images.length" class="view-section">
            <h4>{{ isZh ? '描述海报' : 'Posters' }}</h4>
            <div class="view-images">
              <img v-for="(img, i) in viewProduct.poster_images" :key="'p'+i" :src="img" class="view-img" style="width:160px;height:auto" />
            </div>
          </div>
          <div class="view-grid">
            <div class="view-field"><span class="vf-label">中文标题</span><span class="vf-value">{{ viewProduct.title }}</span></div>
            <div class="view-field"><span class="vf-label">English Title</span><span class="vf-value">{{ viewProduct.title_en || '-' }}</span></div>
            <div v-if="isB2B && viewProduct.factory_name" class="view-field"><span class="vf-label">{{ t('admin.factory') }}</span><span class="vf-value">{{ viewProduct.factory_name }}</span></div>
            <div class="view-field"><span class="vf-label">{{ t('product.category') }}</span><span class="vf-value">{{ viewProduct.category_name || '-' }}</span></div>
            <div class="view-field"><span class="vf-label">{{ t('admin.basePrice') }}</span><span class="vf-value price-hl">${{ viewProduct.base_price }} {{ viewProduct.price_unit }}</span></div>
            <div class="view-field"><span class="vf-label">{{ t('admin.moq') }}</span><span class="vf-value">{{ viewProduct.moq }} {{ t('product.pcs') }}</span></div>
            <div class="view-field"><span class="vf-label">{{ t('product.leadTime') }}</span><span class="vf-value">{{ viewProduct.lead_time || '-' }}</span></div>
            <div class="view-field"><span class="vf-label">{{ t('admin.feature') }}</span><span class="vf-value">{{ viewProduct.is_featured ? 'Yes' : 'No' }}</span></div>
            <div class="view-field"><span class="vf-label">{{ t('admin.setNew') }}</span><span class="vf-value">{{ viewProduct.is_new ? 'Yes' : 'No' }}</span></div>
          </div>
          <div class="view-section" v-if="viewProduct.description"><h4>Description (CN)</h4><p>{{ viewProduct.description }}</p></div>
          <div class="view-section" v-if="viewProduct.description_en"><h4>Description (EN)</h4><p>{{ viewProduct.description_en }}</p></div>
          <div class="view-section" v-if="viewProduct.specs && Object.keys(viewProduct.specs).length">
            <h4>{{ t('product.detail.specs') }}</h4>
            <table class="view-specs"><tr v-for="(v, k) in viewProduct.specs" :key="k"><td class="sk">{{ k }}</td><td>{{ v }}</td></tr></table>
          </div>
          <div class="view-section" v-if="viewProduct.packaging_info"><h4>Packaging (CN)</h4><p>{{ viewProduct.packaging_info }}</p></div>
          <div class="view-section" v-if="viewProduct.packaging_info_en"><h4>Packaging (EN)</h4><p>{{ viewProduct.packaging_info_en }}</p></div>
          <div class="view-section" v-if="viewProduct.customization"><h4>Customization (CN)</h4><p>{{ viewProduct.customization }}</p></div>
          <div class="view-section" v-if="viewProduct.customization_en"><h4>Customization (EN)</h4><p>{{ viewProduct.customization_en }}</p></div>
          <div class="view-section" v-if="viewProduct.video_url"><h4>Video</h4><a :href="viewProduct.video_url" target="_blank" class="view-link">{{ viewProduct.video_url }}</a></div>
          <div class="view-section" v-if="viewProduct.review_note"><h4>{{ viewProduct.status === 'rejected' ? t('admin.rejectReason') : t('admin.offlineReason') }}</h4><p class="view-reject">{{ viewProduct.review_note }}</p></div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useDisplay } from '../../utils/display'
import { useSiteMode } from '../../composables/useSiteMode'
import { ElMessage } from 'element-plus'
import api from '../../api'

const { t } = useI18n()
const { isZh } = useDisplay()
const router = useRouter()
const { isB2B, isB2C, loadSiteMode } = useSiteMode()
const activeTab = ref('')
const stats = ref({})
const factories = ref([])
const products = ref([])
const customers = ref([])
const productFilter = ref('all')
const unreadInquiries = ref(0)
let unreadTimer = null

const showRejectDialog = ref(false)
const rejectTarget = ref(null)
const rejectReason = ref('')

const showOfflineDialog = ref(false)
const offlineTarget = ref(null)
const offlineReason = ref('')

const showViewDialog = ref(false)
const viewProduct = ref(null)

const showFactoryDetail = ref(false)
const factoryDetail = ref(null)
const showRejectFactoryDialog = ref(false)
const rejectFactoryTarget = ref(null)
const rejectFactoryReason = ref('')

const analytics = ref({})

const maxInqByDate = computed(() => Math.max(1, ...((analytics.value.inquiries_by_date || []).map(d => d.count))))
const maxInqByStatus = computed(() => Math.max(1, ...((analytics.value.inquiries_by_status || []).map(d => d.count))))
const maxProdByCat = computed(() => Math.max(1, ...((analytics.value.products_by_category || []).map(d => d.count))))

function barWidth(val, max) { return Math.max(2, (val / max) * 100) + '%' }

function statusLabelInq(s) {
  const map = { new: 'admin.sNew', contacted: 'admin.sContacted', quoted: 'admin.sQuoted', closed: 'admin.sClosed' }
  return t(map[s]) || s
}

function statusColor(s) {
  return { new: 'primary', contacted: 'warning', quoted: 'success', closed: 'info' }[s] || 'primary'
}

function statusType(s) {
  return { active: 'success', pending: 'warning', draft: 'info', rejected: 'danger' }[s] || 'info'
}

function statusLabel(s) {
  const map = { draft: 'admin.sDraft', pending: 'admin.sPending', active: 'admin.sActive', rejected: 'admin.sRejected' }
  return t(map[s]) || s
}

function productStatusLabel(s) {
  const map = { draft: 'admin.sDraft', pending: 'admin.sPending', active: 'admin.sActive', rejected: 'admin.sRejected' }
  return t(map[s]) || s
}

function factoryStatusLabel(s) {
  if (s === 'disabled') return isZh.value ? '已禁用' : 'Disabled'
  const map = { approved: 'factory.approved', pending: 'factory.pending', rejected: 'factory.rejected' }
  return t(map[s]) || s
}

function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d.replace(' ', 'T') + 'Z')
  if (isNaN(dt.getTime())) return d
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

async function loadStats() {
  const { data } = await api.get('/admin/stats')
  stats.value = data
}

async function loadFactories() {
  const { data } = await api.get('/admin/factories')
  factories.value = data
}

async function loadProducts() {
  const params = { status: productFilter.value }
  const { data } = await api.get('/admin/products', { params })
  products.value = data
}

async function loadAnalytics() {
  try {
    const { data } = await api.get('/admin/analytics')
    analytics.value = data
  } catch { analytics.value = {} }
}

async function loadCustomers() {
  try {
    const { data } = await api.get('/inquiries/admin')
    const customerMap = new Map()
    data.items?.forEach(inq => {
      const key = inq.email
      if (!customerMap.has(key)) {
        customerMap.set(key, {
          contact_name: inq.contact_name,
          company_name: inq.company_name,
          email: inq.email,
          phone: inq.phone,
          source: inq.source || '',
          created_at: inq.created_at,
          inquiry_count: 0
        })
      }
      customerMap.get(key).inquiry_count++
    })
    customers.value = Array.from(customerMap.values())
  } catch (e) {
    customers.value = []
  }
}

async function approveFactory(id) {
  try {
    await api.post(`/admin/factories/${id}/approve`, {})
    ElMessage.success(t('admin.approve') + ' ✓')
    loadFactories(); loadStats()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

function openRejectFactoryDialog(row) {
  rejectFactoryTarget.value = row
  rejectFactoryReason.value = ''
  showRejectFactoryDialog.value = true
}

async function confirmRejectFactory() {
  if (!rejectFactoryReason.value.trim()) {
    ElMessage.warning(isZh.value ? '请填写拒绝理由' : 'Please enter a rejection reason')
    return
  }
  try {
    await api.post(`/admin/factories/${rejectFactoryTarget.value.id}/reject`, { reason: rejectFactoryReason.value.trim() })
    showRejectFactoryDialog.value = false
    ElMessage.success(t('admin.reject') + ' ✓')
    loadFactories(); loadStats()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function disableFactory(id) {
  try {
    await api.post(`/admin/factories/${id}/disable`, {})
    ElMessage.success(isZh.value ? '已禁用' : 'Disabled')
    loadFactories(); loadStats()
  } catch (e) {
    console.error('Disable failed:', e)
    ElMessage.error(e.response?.data?.error || 'Failed')
  }
}

async function deleteFactory(id) {
  try {
    await api.delete(`/admin/factories/${id}`)
    ElMessage.success(t('admin.delete') + ' ✓')
    loadFactories(); loadStats()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function enableFactory(id) {
  try {
    await api.post(`/admin/factories/${id}/enable`, {})
    ElMessage.success(isZh.value ? '已启用' : 'Enabled')
    loadFactories(); loadStats()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function openFactoryDetail(row) {
  try {
    const { data } = await api.get(`/admin/factories/${row.id}`)
    factoryDetail.value = data
    showFactoryDetail.value = true
  } catch {
    factoryDetail.value = row
    showFactoryDetail.value = true
  }
}

async function approveProduct(id) {
  await api.post(`/admin/products/${id}/approve`)
  ElMessage.success(isZh.value ? '已通过审核' : 'Approved')
  loadProducts(); loadStats()
}

function openRejectDialog(row) {
  rejectTarget.value = row
  rejectReason.value = ''
  showRejectDialog.value = true
}

async function confirmReject() {
  if (!rejectReason.value.trim()) return
  await api.post(`/admin/products/${rejectTarget.value.id}/reject`, { reason: rejectReason.value.trim() })
  showRejectDialog.value = false
  ElMessage.success(isZh.value ? '已拒绝' : 'Rejected')
  loadProducts(); loadStats()
}

function openOfflineDialog(row) {
  offlineTarget.value = row
  offlineReason.value = ''
  showOfflineDialog.value = true
}

async function confirmOffline() {
  if (!offlineReason.value.trim()) {
    ElMessage.warning(isZh.value ? '请填写下架理由' : 'Please enter a reason for taking offline')
    return
  }
  try {
    await api.post(`/admin/products/${offlineTarget.value.id}/hide`, { reason: offlineReason.value.trim() })
    showOfflineDialog.value = false
    ElMessage.success(t('admin.confirmOffline') + ' ✓')
    loadProducts(); loadStats()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function toggleFeature(id) {
  const { data } = await api.post(`/admin/products/${id}/feature`)
  ElMessage.success(data.is_featured ? (isZh.value ? '已设为爆款' : 'Featured') : (isZh.value ? '已取消爆款' : 'Unfeatured'))
  loadProducts()
}

async function toggleNew(id) {
  const { data } = await api.post(`/admin/products/${id}/new`)
  ElMessage.success(data.is_new ? (isZh.value ? '已设为新品' : 'Set as New') : (isZh.value ? '已取消新品' : 'Unset New'))
  loadProducts()
}
async function toggleBanner(id) {
  const { data } = await api.post(`/admin/products/${id}/banner`)
  ElMessage.success(data.is_banner ? (isZh.value ? '已加入Banner' : 'Added to Banner') : (isZh.value ? '已移出Banner' : 'Removed from Banner'))
  loadProducts()
}

let _actionRow = null
function handleProductAction(cmd, row) {
  _actionRow = row
  if (cmd === 'approve') approveProduct(row.id)
  else if (cmd === 'reject') openRejectDialog(row)
  else if (cmd === 'offline') openOfflineDialog(row)
  else if (cmd === 'activate') activateProduct(row.id)
  else if (cmd === 'feature') toggleFeature(row.id)
  else if (cmd === 'new') toggleNew(row.id)
  else if (cmd === 'banner') toggleBanner(row.id)
  else if (cmd === 'delete') adminDeleteProduct(row.id)
}

async function activateProduct(id) {
  await api.post(`/admin/products/${id}/approve`)
  ElMessage.success(isZh.value ? '已上架' : 'Activated')
  loadProducts(); loadStats()
}

async function adminDeleteProduct(id) {
  await api.delete(`/admin/products/${id}`)
  ElMessage.success(isZh.value ? '已删除' : 'Deleted')
  loadProducts(); loadStats()
}

function editProduct(row) {
  router.push(`/admin/products/${row.id}/edit`)
}

async function openViewDialog(row) {
  try {
    const { data } = await api.get(`/admin/products/${row.id}`)
    viewProduct.value = data
  } catch {
    viewProduct.value = row
  }
  showViewDialog.value = true
}

async function loadUnread() {
  try {
    const { data } = await api.get('/inquiries/admin/unread-count')
    unreadInquiries.value = data.count || 0
  } catch (e) { /* ignore */ }
}

// ── Category management ──
const catList = ref([])
const showCatDialog = ref(false)
const catForm = reactive({ id: null, name: '', name_en: '', parent_id: null, icon: '', sort_order: 0, is_active: true })

const catParentOptions = computed(() => {
  // Top-level categories only, exclude self when editing
  return catList.value.filter(c => !catForm.id || c.id !== catForm.id)
})

async function loadCategories() {
  try {
    const { data } = await api.get('/admin/categories')
    catList.value = data
  } catch { catList.value = [] }
}

function openCatDialog(cat, parentId) {
  if (cat) {
    Object.assign(catForm, { id: cat.id, name: cat.name, name_en: cat.name_en || '', parent_id: cat.parent_id, icon: cat.icon || '', sort_order: cat.sort_order || 0, is_active: cat.is_active !== false })
  } else {
    Object.assign(catForm, { id: null, name: '', name_en: '', parent_id: parentId || null, icon: '', sort_order: 0, is_active: true })
  }
  showCatDialog.value = true
}

async function toggleCatActive(cat) {
  try {
    await api.put(`/admin/categories/${cat.id}`, { is_active: !cat.is_active })
    ElMessage.success(isZh.value ? (cat.is_active ? '已停用' : '已启用') : (cat.is_active ? 'Disabled' : 'Enabled'))
    loadCategories()
    window.dispatchEvent(new CustomEvent('categories-updated'))
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function saveCat() {
  try {
    if (catForm.id) {
      await api.put(`/admin/categories/${catForm.id}`, catForm)
    } else {
      await api.post('/admin/categories', catForm)
    }
    showCatDialog.value = false
    ElMessage.success(isZh.value ? '保存成功' : 'Saved')
    loadCategories()
    window.dispatchEvent(new CustomEvent('categories-updated'))
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function deleteCat(id) {
  try {
    await api.delete(`/admin/categories/${id}`)
    ElMessage.success(isZh.value ? '已删除' : 'Deleted')
    loadCategories()
    window.dispatchEvent(new CustomEvent('categories-updated'))
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

// ── Site Settings ──
const langs = [
  { code: 'zh', name: '中文' }, { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' }, { code: 'ar', name: 'العربية' }, { code: 'ru', name: 'Русский' }
]
const siteSections = [
  { key: 'hero', label: isZh.value ? 'Hero 主标题（每行一个）' : 'Hero Title (one per line)' },
  { key: 'heroDesc', label: isZh.value ? 'Hero 副标题' : 'Hero Description', noGradient: true },
  { key: 'cat', label: isZh.value ? '产品分类' : 'Categories', eyebrowKey: 'cat' },
  { key: 'feat', label: isZh.value ? '热门配置' : 'Featured', eyebrowKey: 'feat' },
  { key: 'new', label: isZh.value ? '新品专区' : 'New Products', eyebrowKey: 'new' },
  { key: 'toys', label: isZh.value ? '玩具精选' : 'Toys Showcase', eyebrowKey: 'toys' },
  { key: 'factory', label: isZh.value ? '工厂直供通道' : 'Factory Direct', eyebrowKey: 'factory' },
  { key: 'work', label: isZh.value ? '合作流程' : 'Process', eyebrowKey: 'work' },
]

// Dynamic items: siteItems[sectionKey][langCode] = [{text, gradient}]
const siteItems = reactive({})
const siteItemsVer = ref(0)
const siteForm = reactive({
  hero_bg_image: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1600&q=80',
  factory_image: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&q=80',
})
const siteSaving = ref(false)

// Factory stats
const factoryStats = reactive([
  { number: '200+', label_zh: '合作工厂', label_en: 'Partner Factories', label_es: 'Fábricas asociadas', label_ar: 'مصانع شريكة', label_ru: 'Фабрик-партнёров' },
  { number: '50+', label_zh: '出口国家', label_en: 'Export Countries', label_es: 'Países de exportación', label_ar: 'دول التصدير', label_ru: 'Стран экспорта' },
  { number: '24h', label_zh: '极速报价', label_en: 'Fast Quotation', label_es: 'Cotización rápida', label_ar: 'عرض سعر سريع', label_ru: 'Быстрый расчёт' },
  { number: '100%', label_zh: '验厂通过率', label_en: 'Audit Pass Rate', label_es: 'Tasa de aprobación', label_ar: 'معدل اجتياز التدقيق', label_ru: 'Прохождение аудита' },
])

// Process steps
const processSteps = reactive([
  { icon: '🔍', title_zh: '浏览选品', title_en: 'Browse & Select', title_es: 'Explorar y Seleccionar', title_ar: 'تصفح واختر', title_ru: 'Просмотр и выбор', desc_zh: '直接从认证制造商采购，无中间商，价格更优。', desc_en: 'Source directly from verified manufacturers. No middlemen, better prices.', desc_es: 'Compre directamente a fabricantes verificados.', desc_ar: 'اشترِ مباشرة من مصنعين معتمدين.', desc_ru: 'Закупайте напрямую у проверенных производителей.' },
  { icon: '📋', title_zh: '询价报价', title_en: 'Request Quote', title_es: 'Solicitar Cotización', title_ar: 'اطلب عرض سعر', title_ru: 'Запрос цены', desc_zh: '产品符合国际标准，发货前提供质检报告。', desc_en: 'Every product meets international standards with pre-shipment inspection.', desc_es: 'Productos que cumplen estándares internacionales.', desc_ar: 'منتجات تلبي المعايير الدولية.', desc_ru: 'Продукция соответствует международным стандартам.' },
  { icon: '🏭', title_zh: '确认订单', title_en: 'Confirm Order', title_es: 'Confirmar Pedido', title_ar: 'تأكيد الطلب', title_ru: 'Подтверждение заказа', desc_zh: '可靠物流覆盖50+国家，整柜、拼柜、空运可选。', desc_en: 'Reliable logistics to 50+ countries. FCL, LCL, air freight available.', desc_es: 'Logística confiable a más de 50 países.', desc_ar: 'لوجستيات موثوقة لأكثر من 50 دولة.', desc_ru: 'Надёжная логистика в 50+ стран.' },
  { icon: '🚢', title_zh: '发货交付', title_en: 'Ship & Deliver', title_es: 'Enviar y Entregar', title_ar: 'الشحن والتسليم', title_ru: 'Отправка и доставка', desc_zh: '专属客户经理，快速响应，专业服务。', desc_en: 'Dedicated account managers with quick response and professional service.', desc_es: 'Gerentes de cuenta dedicados con respuesta rápida.', desc_ar: 'مديرو حسابات مخصصون مع استجابة سريعة.', desc_ru: 'Персональные менеджеры с быстрым откликом.' },
])

// Default items per section per language
const siteDefaults = {
  hero: { zh: [{text:'优质',gradient:false},{text:'智能化',gradient:true},{text:'采购平台',gradient:false}], en: [{text:'Premium',gradient:false},{text:'Automated',gradient:true},{text:'Sourcing.',gradient:false}], es: [{text:'Abastecimiento',gradient:false},{text:'Automatizado',gradient:true},{text:'Premium.',gradient:false}], ar: [{text:'توريد',gradient:false},{text:'آلي',gradient:true},{text:'متميز.',gradient:false}], ru: [{text:'Премиум',gradient:false},{text:'Автоматизированные',gradient:true},{text:'Закупки.',gradient:false}] },
  heroDesc: { zh: [{text:'玩具、无人机、小家电 — 工厂直供价格，低起订量，品质保障，全球50+国家配送。',gradient:false}], en: [{text:'Toys, Drones & Home Appliances — Factory prices, low MOQ, quality assured, global shipping to 50+ countries.',gradient:false}], es: [{text:'Juguetes, Drones y Electrodomésticos — Precios de fábrica, MOQ bajo, calidad garantizada, envío global a más de 50 países.',gradient:false}], ar: [{text:'ألعاب وطائرات بدون طيار وأجهزة منزلية — أسعار المصنع، حد أدنى منخفض، جودة مضمونة، شحن عالمي لأكثر من 50 دولة.',gradient:false}], ru: [{text:'Игрушки, дроны и бытовая техника — заводские цены, низкий MOQ, гарантия качества, доставка в 50+ стран.',gradient:false}] },
  cat: { zh: [{text:'多种',gradient:true},{text:'选择',gradient:false}], en: [{text:'Multiple',gradient:true},{text:'Choices',gradient:false}], es: [{text:'Múltiples',gradient:true},{text:'Opciones',gradient:false}], ar: [{text:'خيارات',gradient:true},{text:'متعددة',gradient:false}], ru: [{text:'Множество',gradient:true},{text:'Вариантов',gradient:false}] },
  feat: { zh: [{text:'热门',gradient:false},{text:'配置',gradient:true}], en: [{text:'Trending',gradient:false},{text:'Configurations',gradient:true}], es: [{text:'Configuraciones',gradient:false},{text:'Tendencia',gradient:true}], ar: [{text:'تكوينات',gradient:false},{text:'رائجة',gradient:true}], ru: [{text:'Трендовые',gradient:false},{text:'Конфигурации',gradient:true}] },
  new: { zh: [{text:'新品',gradient:true},{text:'专区',gradient:false}], en: [{text:'New',gradient:true},{text:'Arrivals',gradient:false}], es: [{text:'Nuevos',gradient:true},{text:'Productos',gradient:false}], ar: [{text:'جديد',gradient:true},{text:'وصل',gradient:false}], ru: [{text:'Новые',gradient:true},{text:'Товары',gradient:false}] },
  toys: { zh: [{text:'玩具',gradient:false},{text:'精选',gradient:true}], en: [{text:'Toys',gradient:false},{text:'Showcase',gradient:true}], es: [{text:'Juguetes',gradient:false},{text:'Escaparate',gradient:true}], ar: [{text:'الألعاب',gradient:false},{text:'عرض',gradient:true}], ru: [{text:'Игрушки',gradient:false},{text:'Витрина',gradient:true}] },
  factory: { zh: [{text:'工厂',gradient:false},{text:'直供',gradient:true},{text:'通道',gradient:false}], en: [{text:'Factory',gradient:false},{text:'Direct',gradient:true},{text:'Access',gradient:false}], es: [{text:'Acceso',gradient:false},{text:'Directo',gradient:true},{text:'de Fábrica',gradient:false}], ar: [{text:'وصول',gradient:false},{text:'مباشر',gradient:true},{text:'للمصنع',gradient:false}], ru: [{text:'Прямой',gradient:false},{text:'Доступ',gradient:true},{text:'к Фабрике',gradient:false}] },
  work: { zh: [{text:'高效',gradient:false},{text:'工作流',gradient:true}], en: [{text:'The Quantum',gradient:false},{text:'Workflow',gradient:true}], es: [{text:'El Flujo',gradient:false},{text:'Cuántico',gradient:true}], ar: [{text:'سير العمل',gradient:false},{text:'الكمي',gradient:true}], ru: [{text:'Квантовый',gradient:false},{text:'Процесс',gradient:true}] },
}

function initSiteItems() {
  for (const sec of siteSections) {
    siteItems[sec.key] = {}
    for (const lang of langs) {
      const def = siteDefaults[sec.key]?.[lang.code] || [{text:'',gradient:false}]
      siteItems[sec.key][lang.code] = def.map(d => ({...d}))
    }
  }
  siteItemsVer.value++
}

function getSectionItems(secKey, langCode) {
  void siteItemsVer.value
  return siteItems[secKey]?.[langCode] || []
}
function addSectionItem(secKey, langCode) {
  if (!siteItems[secKey]) siteItems[secKey] = {}
  if (!siteItems[secKey][langCode]) siteItems[secKey][langCode] = []
  siteItems[secKey][langCode].push({ text: '', gradient: false })
  siteItemsVer.value++
}
function removeSectionItem(secKey, langCode, idx) {
  siteItems[secKey][langCode].splice(idx, 1)
  siteItemsVer.value++
}

async function loadSiteSettings() {
  initSiteItems()
  // Init eyebrow defaults
  const eyebrowDefaults = {
    cat: { zh:'产品分类', en:'PRODUCT CATEGORIES', es:'CATEGORÍAS', ar:'فئات المنتجات', ru:'КАТЕГОРИИ' },
    feat: { zh:'精选推荐', en:'FEATURED SELECTION', es:'SELECCIÓN DESTACADA', ar:'اختيار مميز', ru:'ИЗБРАННОЕ' },
    new: { zh:'新品上架', en:'JUST ARRIVED', es:'RECIÉN LLEGADOS', ar:'وصل حديثاً', ru:'НОВИНКИ' },
    toys: { zh:'精选专区', en:'SPECIALTY', es:'ESPECIALIDAD', ar:'تخصص', ru:'СПЕЦИАЛЬНОЕ' },
    factory: { zh:'直接采购', en:'DIRECT SOURCING', es:'ABASTECIMIENTO DIRECTO', ar:'توريد مباشر', ru:'ПРЯМЫЕ ЗАКУПКИ' },
    work: { zh:'合作流程', en:'HOW IT WORKS', es:'CÓMO FUNCIONA', ar:'كيف يعمل', ru:'КАК ЭТО РАБОТАЕТ' },
  }
  for (const [sec, vals] of Object.entries(eyebrowDefaults)) {
    for (const [lang, val] of Object.entries(vals)) {
      siteForm['eyebrow_' + sec + '.' + lang] = val
    }
  }
  // Init factory desc defaults
  const factDescDefaults = { zh:'所有工厂均经过审核并获得质量标准认证', en:'All factories audited and certified for quality standards', es:'Todas las fábricas auditadas y certificadas', ar:'جميع المصانع مدققة ومعتمدة', ru:'Все фабрики проверены и сертифицированы' }
  for (const [lang, val] of Object.entries(factDescDefaults)) {
    siteForm['factory_desc.' + lang] = val
  }
  try {
    const { data } = await api.get('/site-settings')
    if (data.hero_bg_image) siteForm.hero_bg_image = data.hero_bg_image
    if (data.factory_image) siteForm.factory_image = data.factory_image
    // Title items
    for (const sec of siteSections) {
      for (const lang of langs) {
        const raw = data[`${sec.key}.${lang.code}`]
        if (raw) {
          try { siteItems[sec.key][lang.code] = JSON.parse(raw) } catch {}
        }
      }
    }
    // Eyebrows
    for (const sec of siteSections) {
      if (!sec.eyebrowKey) continue
      for (const lang of langs) {
        const val = data[`eyebrow_${sec.eyebrowKey}.${lang.code}`]
        if (val) siteForm[`eyebrow_${sec.eyebrowKey}.${lang.code}`] = val
      }
    }
    // Factory desc
    for (const lang of langs) {
      const val = data[`factory_desc.${lang.code}`]
      if (val) siteForm[`factory_desc.${lang.code}`] = val
    }
    // Factory stats
    if (data.factory_stats) {
      try { Object.assign(factoryStats, JSON.parse(data.factory_stats)) } catch {}
    }
    // Process steps
    if (data.process_steps) {
      try { Object.assign(processSteps, JSON.parse(data.process_steps)) } catch {}
    }
  } catch (e) { /* use defaults */ }
}

async function uploadHeroBg(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    siteForm.hero_bg_image = data.url
    ElMessage.success(file.name + ' ✓')
  } catch { ElMessage.error('Upload failed') }
  e.target.value = ''
}
async function uploadFactoryImg(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    siteForm.factory_image = data.url
    ElMessage.success(file.name + ' ✓')
  } catch { ElMessage.error('Upload failed') }
  e.target.value = ''
}
async function uploadStepIcon(e, idx) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    processSteps[idx].icon = data.url
    ElMessage.success(file.name + ' ✓')
  } catch { ElMessage.error('Upload failed') }
  e.target.value = ''
}

async function saveSiteSettings() {
  siteSaving.value = true
  try {
    const payload = { hero_bg_image: siteForm.hero_bg_image, factory_image: siteForm.factory_image }
    // Title items
    for (const sec of siteSections) {
      for (const lang of langs) {
        payload[`${sec.key}.${lang.code}`] = JSON.stringify(siteItems[sec.key][lang.code])
      }
    }
    // Eyebrows
    for (const sec of siteSections) {
      if (!sec.eyebrowKey) continue
      for (const lang of langs) {
        payload[`eyebrow_${sec.eyebrowKey}.${lang.code}`] = siteForm[`eyebrow_${sec.eyebrowKey}.${lang.code}`] || ''
      }
    }
    // Factory desc
    for (const lang of langs) {
      payload[`factory_desc.${lang.code}`] = siteForm[`factory_desc.${lang.code}`] || ''
    }
    // Factory stats & process steps as JSON
    payload.factory_stats = JSON.stringify([...factoryStats])
    payload.process_steps = JSON.stringify([...processSteps])
    await api.put('/admin/site-settings', payload)
    ElMessage.success(isZh.value ? '保存成功' : 'Saved')
  } catch (e) { ElMessage.error('Failed') }
  finally { siteSaving.value = false }
}

onMounted(async () => {
  await loadSiteMode()
  // 根据模式设置默认标签
  if (isB2C.value) {
    activeTab.value = 'b2c-products'
  } else {
    activeTab.value = 'factories'
  }
  loadStats(); loadFactories(); loadProducts(); loadCustomers(); loadAnalytics(); loadCategories(); loadSiteSettings()
  loadUnread()
  unreadTimer = setInterval(loadUnread, 8000)
  window.addEventListener('site-mode-changed', onSiteModeChanged)
})
onUnmounted(() => {
  if (unreadTimer) clearInterval(unreadTimer)
  window.removeEventListener('site-mode-changed', onSiteModeChanged)
})

function onSiteModeChanged() {
  loadSiteMode()
  // 切换到B2C模式时，如果当前在工厂或商品审核标签，切换到其他标签
  if (isB2C.value && (activeTab.value === 'factories' || activeTab.value === 'products')) {
    activeTab.value = 'b2c-products'
  }
}
</script>

<style scoped>
.admin-dash { padding: 32px 0; min-height: 100vh; margin-top: -96px; padding-top: 120px; }
.admin-dash > .container { max-width: 1280px; }
.prod-cell { display: flex; align-items: center; gap: 10px; }
.prod-thumb { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; background: #f9fafb; flex-shrink: 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
.dash-header h1 { font-size: 28px; font-weight: 800; }
.nav-links { display: flex; gap: 8px; }
.nav-links a {
  color: #6b7280; font-weight: 600; font-size: 14px; padding: 8px 18px;
  border-radius: 9999px; transition: all .2s;
}
.nav-links a:hover { background: #f3f4f6; color: #111827; }
.nav-links .nav-active { background: var(--primary); color: #fff; }
.nav-links .nav-active:hover { background: var(--primary-hover); }
.nav-inq { position: relative; }
.nav-badge {
  display: inline-flex; align-items: center; justify-content: center;
  background: #ef4444; color: #fff; font-size: 10px; font-weight: 700;
  min-width: 18px; height: 18px; border-radius: 9px; padding: 0 4px;
  margin-left: 4px; vertical-align: middle;
}

/* Stats */
.stats-grid { display: flex; gap: 14px; margin-bottom: 28px; flex-wrap: wrap; }
.stat-card {
  flex: 1; min-width: 120px; background: #fff; border: 1px solid #e5e7eb;
  border-radius: 14px; padding: 22px; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
  transition: all .2s;
}
.stat-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.07); transform: translateY(-2px); }
.stat-card span:last-child { font-size: 12px; color: #9ca3af; display: block; margin-top: 6px; }
.stat-num { font-size: 30px; font-weight: 800; }
.stat-num.warn { color: var(--warning); }
.stat-num.ok { color: var(--success); }
.stat-num.blue { color: var(--primary); }
.stat-num.danger { color: var(--danger); }

/* Tabs card */
.fade-up-d2 {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,.04); overflow: hidden;
  padding: 0;
}
:deep(.el-tabs__header) { margin-bottom: 0; padding: 6px 24px 0; }
:deep(.el-tabs__content) { padding: 24px; }

.filter-bar { margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.price-admin { font-weight: 700; color: var(--success); white-space: nowrap; }
.no-wrap-col .cell { white-space: nowrap; }

/* Analytics */
.analytics-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.chart-section {
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 14px; padding: 22px;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.chart-section:hover { box-shadow: 0 6px 20px rgba(0,0,0,.07); }
.chart-section h3 { font-size: 15px; font-weight: 700; margin-bottom: 14px; }
.bar-chart { display: flex; flex-direction: column; gap: 10px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-label { width: 90px; font-size: 12px; color: #9ca3af; text-align: right; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-track { flex: 1; height: 22px; background: #f3f4f6; border-radius: 6px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 6px; transition: width .5s ease; min-width: 4px; }
.bar-fill.primary { background: var(--primary); }
.bar-fill.success { background: var(--success); }
.bar-fill.warning { background: var(--warning); }
.bar-fill.info { background: #9ca3af; }
.bar-value { width: 36px; font-size: 13px; font-weight: 700; color: #111827; }
.empty-chart { height: 120px; display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 14px; background: #f9fafb; border-radius: 10px; }

/* Dialogs */
.factory-detail .detail-row { margin-bottom: 12px; font-size: 14px; }
.factory-detail .detail-row strong { color: #9ca3af; margin-inline-end: 8px; }
.cert-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.cert-link { display: inline-block; padding: 4px 12px; background: var(--primary-light); color: var(--primary); border-radius: 8px; font-size: 13px; font-weight: 600; transition: all .2s; }
.cert-link:hover { background: var(--primary); color: #fff; }
.view-detail { max-height: 70vh; overflow-y: auto; }
.view-images { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.view-img { width: 120px; height: 120px; object-fit: cover; border-radius: 10px; border: 1px solid #e5e7eb; }
.view-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
.view-field { background: #f9fafb; border-radius: 10px; padding: 12px 16px; }
.vf-label { display: block; font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.vf-value { font-size: 15px; font-weight: 600; }
.price-hl { color: var(--success); }
.view-section { margin-bottom: 16px; }
.view-section h4 { font-size: 14px; font-weight: 700; color: #9ca3af; margin-bottom: 6px; }
.view-section p { font-size: 14px; line-height: 1.7; }
.view-specs { width: 100%; border-collapse: collapse; }
.view-specs td { padding: 8px 12px; font-size: 13px; }
.view-specs tr:nth-child(even) { background: #f9fafb; }
.view-specs .sk { color: #9ca3af; width: 40%; }
.view-link { color: var(--primary); font-size: 14px; word-break: break-all; }
.view-reject { color: var(--danger); font-weight: 600; }
/* Category management */
.cat-tree-list { display: flex; flex-direction: column; gap: 10px; }
.cat-tree-row { background: #f9fafb; border-radius: 12px; overflow: hidden; }
.cat-row-main {
  display: flex; align-items: center; gap: 10px; padding: 14px 18px;
  font-size: 14px;
}
.cat-row-child {
  display: flex; align-items: center; gap: 10px; padding: 10px 18px 10px 48px;
  font-size: 13px; background: #fff;
}
.cat-row-child + .cat-row-child { border-top: 1px solid #f3f4f6; }
.cat-row-icon { font-size: 20px; flex-shrink: 0; }
.cat-row-name { font-weight: 600; }
.cat-row-en { color: #9ca3af; font-size: 12px; }
.cat-row-order { color: #d1d5db; font-size: 12px; font-weight: 500; }
.cat-label { display: block; font-size: 13px; font-weight: 600; color: #6b7280; margin-bottom: 6px; }
.site-img-upload { display: flex; gap: 8px; align-items: center; }
.site-img-preview { margin-top: 12px; max-width: 100%; max-height: 160px; border-radius: 12px; object-fit: cover; border: 0.5px solid rgba(15,23,42,.08); }
.site-mgmt { max-width: 800px; }
.site-section { margin-bottom: 32px; padding: 24px; background: #fff; border: 0.5px solid rgba(15,23,42,.05); border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.02); }
.site-section h3 { font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #0F172A; }
.site-title-editor { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.site-title-editor.hero-layout { flex-direction: column; align-items: stretch; }
.site-title-item { display: flex; align-items: center; gap: 6px; }
.hero-layout .site-title-item { width: 100%; }
.gradient-check { margin-left: 0 !important; }
.gradient-check :deep(.el-checkbox__label) { font-size: 11px; color: #7000ff; }
.gradient-hint { color: #7000ff; font-size: 11px; }
.lang-tabs :deep(.el-tabs__header) { margin-bottom: 12px; }
.lang-tabs :deep(.el-tabs__item) { font-size: 12px !important; padding: 0 12px !important; }
.site-label { display: block; font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 8px; }
.site-lang-tag { font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; min-width: 24px; }
.site-eyebrow-row { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 0.5px solid rgba(15,23,42,.05); }
.site-eyebrow-langs { display: flex; flex-wrap: wrap; gap: 8px; }
.site-eyebrow-item { display: flex; align-items: center; gap: 4px; flex: 1; min-width: 140px; }
.site-stat-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px; padding: 10px; background: #f8fafc; border-radius: 10px; }
.site-stat-lang { display: flex; align-items: center; gap: 4px; flex: 1; min-width: 120px; }
.site-step-row { padding: 14px; background: #f8fafc; border-radius: 12px; margin-bottom: 12px; }
.site-step-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.site-step-num { font-size: 20px; font-weight: 800; color: #d1d5db; }
.site-step-preview { width: 36px; height: 36px; object-fit: contain; border-radius: 8px; border: 0.5px solid rgba(15,23,42,.08); }
</style>
