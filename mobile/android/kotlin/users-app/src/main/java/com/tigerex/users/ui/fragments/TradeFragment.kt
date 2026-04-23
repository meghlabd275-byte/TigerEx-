package com.tigerex.users.app.ui.fragments

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.tabs.TabLayoutMediator
import com.tigerex.users.app.databinding.FragmentTradeBinding
import com.tigerex.users.app.ui.MainActivity

class TradeFragment : Fragment() {
    
    private var _binding: FragmentTradeBinding? = null
    private val binding get() = _binding!!
    
    private val tradingModes = listOf(
        "Spot" to "Spot",
        "Futures" to "Futures",
        "Margin" to "Margin",
        "Option" to "Options",
        "Alpha" to "Alpha",
        "Copy" to "Copy",
        "TradeX" to "TradeX"
    )
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentTradeBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupViewPager()
    }
    
    private fun setupViewPager() {
        binding.viewPager.adapter = TradingPagerAdapter(this)
        
        TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
            tab.text = tradingModes[position].first
        }.attach()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
    
    // Inner Pager Adapter
    inner class TradingPagerAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {
        override fun getItemCount(): Int = tradingModes.size
        
        override fun createFragment(position: Int): Fragment {
            return when (position) {
                0 -> SpotTradeFragment()
                1 -> FuturesTradeFragment()
                2 -> MarginTradeFragment()
                3 -> OptionTradeFragment()
                4 -> AlphaTradeFragment()
                5 -> CopyTradeFragment()
                6 -> TradeXFragment()
                else -> SpotTradeFragment()
            }
        }
    }
}

// ============ SPOT TRADE ============
class SpotTradeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_spot_trade, container, false)
    }
}

// ============ FUTURES TRADE ============
class FuturesTradeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_futures_trade, container, false)
    }
}

// ============ MARGIN TRADE ============
class MarginTradeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_margin_trade, container, false)
    }
}

// ============ OPTIONS TRADE ============
class OptionTradeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_option_trade, container, false)
    }
}

// ============ ALPHA TRADE ============
class AlphaTradeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_alpha_trade, container, false)
    }
}

// ============ COPY TRADE ============
class CopyTradeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_copy_trade, container, false)
    }
}

// ============ TRADE X ============
class TradeXFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_tradex_trade, container, false)
    }
}

// ============ TRADFI FRAGMENT ============
class TradFiFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_tradfi, container, false)
    }
}

// ============ ASSETS FRAGMENT ============
class AssetsFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_assets, container, false)
    }
}

// ============ MARKETS FRAGMENT ============
class MarketsFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_markets, container, false)
    }
}

// ============ HOME FRAGMENT ============
class HomeFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return inflater.inflate(com.tigerex.users.app.R.layout.fragment_home, container, false)
    }
}